# File: PyEGRO/sensitivity/sobol.py

import os
import numpy as np
import torch
import gpytorch
import warnings
import json
import joblib
import pandas as pd
from SALib.sample.sobol import sample
from SALib.analyze.sobol import analyze
from typing import Dict, List, Optional, Union, Callable
import matplotlib.pyplot as plt
from dataclasses import dataclass
from rich.progress import Progress, TextColumn, BarColumn
from rich.progress import TaskProgressColumn, TimeRemainingColumn
from rich.progress import TimeElapsedColumn, SpinnerColumn
from rich.console import Console
from rich.table import Table
from pathlib import Path

# Configure matplotlib
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14

# Suppress warnings
warnings.filterwarnings("ignore", category=gpytorch.utils.warnings.GPInputWarning)

class GPRegressionModel(gpytorch.models.ExactGP):
    """GPyTorch model class for Gaussian Process Regression."""
    def __init__(self, train_x: torch.Tensor, train_y: torch.Tensor, 
                 likelihood: gpytorch.likelihoods.Likelihood):
        super().__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(
            gpytorch.kernels.MaternKernel(
                nu=2.5,
                ard_num_dims=train_x.size(-1)
            )
        )

        # Initial Hyperparameters
        self.covar_module.base_kernel.lengthscale = 1.0  
        self.covar_module.outputscale = 1.0  
        self.likelihood.noise_covar.noise = 1e-4  

    def forward(self, x: torch.Tensor) -> gpytorch.distributions.MultivariateNormal:
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)

class DeviceAgnosticGPR:
    """Device-agnostic GPR model handler."""
    
    def __init__(self, prefer_gpu: bool = False):
        self.prefer_gpu = prefer_gpu
        self.device = self._get_device()
        self.model = None
        self.scaler_X = None
        self.scaler_y = None
        
        self._print_device_info()
    
    def _get_device(self) -> torch.device:
        if self.prefer_gpu and torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")
    
    def _print_device_info(self):
        if self.device.type == "cuda":
            device_name = torch.cuda.get_device_name(0)
            memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"\nUsing GPU: {device_name}")
            print(f"GPU Memory: {memory_gb:.1f} GB")
            print(f"CUDA Version: {torch.version.cuda}")
        else:
            import psutil
            import cpuinfo
            
            cpu_info = cpuinfo.get_cpu_info()
            device_name = cpu_info.get('brand_raw', 'Unknown CPU')
            
            memory_gb = psutil.virtual_memory().total / 1024**3
            print(f"\nUsing CPU: {device_name}")
            print(f"System Memory: {memory_gb:.1f} GB")
        
        print(f"PyTorch Version: {torch.__version__}")
        print(f"GPyTorch Version: {gpytorch.__version__}\n")

    def load_model(self, model_dir: str = 'RESULT_MODEL_GPR') -> bool:
        """Load model using state dict approach."""
        try:
            # Load scalers
            self.scaler_X = joblib.load(os.path.join(model_dir, 'scaler_X.pkl'))
            self.scaler_y = joblib.load(os.path.join(model_dir, 'scaler_y.pkl'))
            
            # Load state dict
            state_dict = torch.load(
                os.path.join(model_dir, 'gpr_model.pth'),
                map_location=self.device
            )
            
            # Initialize model components
            likelihood = gpytorch.likelihoods.GaussianLikelihood()
            
            # Create new model instance
            train_x = state_dict['train_inputs'][0].to(self.device)
            train_y = state_dict['train_targets'].to(self.device)
            self.model = GPRegressionModel(train_x, train_y, likelihood)
            
            # Load state dicts
            self.model.load_state_dict(state_dict['model'])
            self.model.likelihood.load_state_dict(state_dict['likelihood'])
            
            # Move to device and set evaluation mode
            self.model = self.model.to(self.device)
            self.model.likelihood = self.model.likelihood.to(self.device)
            self.model.eval()
            self.model.likelihood.eval()
            
            print(f"Model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

    def predict(self, X: np.ndarray, batch_size: int = 1000) -> np.ndarray:
        """Make predictions with improved stability."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model first.")
            
        n_samples = X.shape[0]
        predictions = np.zeros(n_samples)
        X_scaled = self.scaler_X.transform(X)
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category="linear_operator.utils.warnings.NumericalWarning")
            with gpytorch.settings.fast_pred_var(), \
                gpytorch.settings.cholesky_jitter(1e-3), \
                gpytorch.settings.max_cholesky_size(2000):
                
                for i in range(0, n_samples, batch_size):
                    end_idx = min(i + batch_size, n_samples)
                    X_batch = torch.tensor(
                        X_scaled[i:end_idx], 
                        dtype=torch.float32
                    ).to(self.device)
                    
                    with torch.no_grad():
                        try:
                            output = self.model(X_batch)
                            pred_batch = output.mean.cpu().numpy()
                        except RuntimeError as e:
                            if "not positive definite" in str(e):
                                with gpytorch.settings.cholesky_jitter(1e-1):
                                    output = self.model(X_batch)
                                    pred_batch = output.mean.cpu().numpy()
                    
                    pred_batch = self.scaler_y.inverse_transform(
                        pred_batch.reshape(-1, 1)
                    ).flatten()
                    predictions[i:end_idx] = pred_batch
                    
        return predictions












@dataclass
class Variable:
    """Class to represent a variable for sensitivity analysis."""
    name: str
    bounds: List[float]
    description: Optional[str] = ""

class SobolAnalyzer:
    """
    SobolAnalyzer: A class for performing Sobol sensitivity analysis.
    
    Display Options:
    --------------
    show_progress : bool = True
        Show progress during analysis
        - Sample generation progress
        - Evaluation progress
        - Time elapsed/remaining
    
    show_result : bool = True
        Show final results after completion
        - Summary of sensitivity indices
        - Visualization information
        - File save locations
        
    Options for Use:
    --------------
    1. With InitialDesign:
        analyzer = SobolAnalyzer.from_initial_design(design)
        
    2. With data_info.json:
        analyzer = SobolAnalyzer(data_info_path="path/to/data_info.json")
        
    3. With surrogate model:
        analyzer = SobolAnalyzer(
            model_path="path/to/model",
            data_info_path="path/to/data_info.json"
        )
    """
    
    def __init__(
        self,
        output_dir: str = 'SENSITIVITY_ANALYSIS',
        data_info_path: Optional[str] = None,
        model_path: Optional[str] = None,
        show_progress: bool = True,
        show_result: bool = True,
        device: Optional[str] = None
    ):
        """Initialize the SobolAnalyzer."""
        self.output_dir = output_dir
        self.show_progress = show_progress
        self.show_result = show_result
        self.device = self._get_device(device)
        self.variables = []
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize model components
        self.gpr_handler = None
        
        # Load data info if provided
        if data_info_path:
            self.load_data_info(data_info_path)
        
        # Load model if provided
        if model_path:
            self._load_surrogate_model(model_path)
        
        # Setup rich console
        self.console = Console()
    
    def _get_device(self, device: Optional[str]) -> torch.device:
        """Determine the computing device."""
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        return torch.device(device)
    
    @classmethod
    def from_initial_design(cls, design, output_dir: str = 'SENSITIVITY_ANALYSIS'):
        """Create analyzer from InitialDesign instance."""
        analyzer = cls(output_dir=output_dir)
        
        # Convert design variables to sensitivity variables
        for var in design.variables:
            if 'range' in var:  # Design variable
                bounds = var['range']
            elif 'low' in var:  # Uniform env variable
                bounds = [var['low'], var['high']]
            else:  # Normal/lognormal env variable
                std = var['mean'] * var['cov']
                bounds = [var['mean'] - 3*std, var['mean'] + 3*std]
            
            analyzer.add_variable(
                name=var['name'],
                bounds=bounds,
                description=var.get('description', '')
            )
        
        return analyzer
    
    def add_variable(
        self,
        name: str,
        bounds: List[float],
        description: str = ""
    ) -> None:
        """Add a variable for sensitivity analysis."""
        var = Variable(name=name, bounds=bounds, description=description)
        self.variables.append(var)
    
    def load_data_info(self, data_info_path: str) -> None:
        """Load variable information from data_info.json."""
        with open(data_info_path, 'r') as f:
            data_info = json.load(f)
        
        for var in data_info['variables']:
            if 'range' in var:  # Design variable
                bounds = var['range']
            elif 'low' in var:  # Uniform env variable
                bounds = [var['low'], var['high']]
            else:  # Normal/lognormal env variable
                std = var['mean'] * var['cov']
                bounds = [var['mean'] - 3*std, var['mean'] + 3*std]
            
            self.add_variable(
                name=var['name'],
                bounds=bounds,
                description=var.get('description', '')
            )
    
    def _load_surrogate_model(self, model_path: str) -> None:
        """Load the surrogate model."""
        self.gpr_handler = DeviceAgnosticGPR(prefer_gpu=(self.device.type == "cuda"))
        success = self.gpr_handler.load_model(model_path)
        
        if not success:
            raise RuntimeError("Failed to load surrogate model")
    
    def prepare_problem(self) -> Dict:
        """Prepare the problem definition for Sobol analysis."""
        if not self.variables:
            raise ValueError("No variables defined. Add variables or load data_info.")
        
        return {
            'num_vars': len(self.variables),
            'names': [var.name for var in self.variables],
            'bounds': [var.bounds for var in self.variables]
        }
    
    def run_analysis(
            self,
            true_func: Optional[Callable] = None,
            n_samples: int = 8192,
            sample_sizes: Optional[List[int]] = None,
            seed: int = 42,
            calc_second_order: bool = False
        ) -> Dict:
            """Run Sobol sensitivity analysis.

            Parameters
            ----------
            true_func : Optional[Callable]
                True function for evaluation. If None, uses surrogate model
            n_samples : int
                Base sample size (will be multiplied based on Sobol requirements)
            sample_sizes : Optional[List[int]]
                List of base sample sizes for convergence analysis
            seed : int
                Random seed for reproducibility
            calc_second_order : bool
                Whether to calculate second-order sensitivity indices

            Returns
            -------
            Dict
                Dictionary containing analysis results
            """
            if true_func is None and self.gpr_handler is None:
                raise ValueError("Either true_func or model_path must be provided")
            
            # Set random seeds
            np.random.seed(seed)
            torch.manual_seed(seed)
            
            # Prepare problem
            problem = self.prepare_problem()
            
            # Set sample sizes
            if sample_sizes is None:
                sample_sizes = [2**n for n in range(4, int(np.log2(n_samples))+1)]
            
            # Create progress context
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                TextColumn("[cyan]{task.fields[info]}"),
                disable=not self.show_progress
            ) as progress:
                
                results = {}
                main_task = progress.add_task(
                    "[white]Running sensitivity analysis...",
                    total=len(sample_sizes),
                    info="Initializing..."
                )
                
                for n in sample_sizes:
                    progress.update(
                        main_task,
                        description=f"[white]Analyzing with {n} samples...",
                        info=f"Generating samples..."
                    )
                    
                    # Generate samples - SALib will generate N*(2D+2) samples if calc_second_order=False
                    # or N*(2D+2+((D-1)*D)/2) samples if calc_second_order=True, where D is num_vars
                    X = sample(problem, n, calc_second_order=calc_second_order)
                    
                    # Evaluate samples
                    if true_func is not None:
                        Y = true_func(X)
                    else:
                        Y = self.gpr_handler.predict(X)
                    
                    # Compute indices
                    Si = analyze(
                        problem, 
                        Y, 
                        calc_second_order=calc_second_order,
                        print_to_console=False
                    )
                    
                    results[n] = {
                        'S1': Si['S1'].tolist(),
                        'ST': Si['ST'].tolist(),
                        'S1_conf': Si['S1_conf'].tolist(),
                        'ST_conf': Si['ST_conf'].tolist()
                    }
                    
                    if calc_second_order:
                        results[n].update({
                            'S2': Si['S2'].tolist(),
                            'S2_conf': Si['S2_conf'].tolist()
                        })
                    
                    progress.update(main_task, advance=1)
            
            # Save and display results
            self._save_results(results)
            
            return results
    
    def _save_results(self, results: Dict) -> None:
        """Save analysis results."""
        # Get variable names
        var_names = [var.name for var in self.variables]
        
        # Save raw results
        with open(f'{self.output_dir}/sobol_results.json', 'w') as f:
            json.dump(results, f, indent=4)
        
        # Get final results
        final_n = max(results.keys())
        final_results = results[final_n]
        
        # Save to CSV
        df = pd.DataFrame({
            'Variable': var_names,
            'S1': final_results['S1'],
            'ST': final_results['ST'],
            'S1_conf': final_results['S1_conf'],
            'ST_conf': final_results['ST_conf']
        })
        df.to_csv(f'{self.output_dir}/sensitivity_indices.csv', index=False)
        
        # Create visualizations
        self._plot_convergence(results, var_names)
        self._plot_indices(
            np.array(final_results['S1']),
            np.array(final_results['ST']),
            np.array(final_results['S1_conf']),
            np.array(final_results['ST_conf']),
            var_names
        )
        
        # Show results if enabled
        if self.show_result:
            self._print_summary(results)
    
    def _plot_convergence(self, results: Dict, variable_names: List[str]) -> None:
        """Plot convergence of sensitivity indices."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        sample_sizes = sorted(list(results.keys()))
        
        for i, var in enumerate(variable_names):
            S1_values = [results[n]['S1'][i] for n in sample_sizes]
            S1_conf = [results[n]['S1_conf'][i] for n in sample_sizes]
            ax1.errorbar(sample_sizes, S1_values, yerr=S1_conf,
                        marker='o', label=var, capsize=5)
            
            ST_values = [results[n]['ST'][i] for n in sample_sizes]
            ST_conf = [results[n]['ST_conf'][i] for n in sample_sizes]
            ax2.errorbar(sample_sizes, ST_values, yerr=ST_conf,
                        marker='o', label=var, capsize=5)
        
        for ax in [ax1, ax2]:
            ax.set_xscale('log')
            ax.set_xlabel('Number of Samples')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        ax1.set_ylabel('First Order Index')
        ax2.set_ylabel('Total Order Index')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/convergence_plot.png', dpi=300,
                   bbox_inches='tight')
        plt.close()
    
    def _plot_indices(
        self,
        S1: np.ndarray,
        ST: np.ndarray,
        S1_conf: np.ndarray,
        ST_conf: np.ndarray,
        variable_names: List[str]
    ) -> None:
        """Plot final sensitivity indices."""
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.arange(len(variable_names))
        
        ax.bar(x - 0.2, S1, 0.4, label='First Order',
               yerr=S1_conf, capsize=5)
        ax.bar(x + 0.2, ST, 0.4, label='Total Order',
               yerr=ST_conf, capsize=5)
        
        ax.set_xticks(x)
        ax.set_xticklabels(variable_names, rotation=45, ha='right')
        ax.set_ylabel('Sensitivity Index')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/sensitivity_indices.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _print_summary(self, results: Dict) -> None:
        """Print summary of sensitivity analysis results."""
        final_n = max(results.keys())
        final_results = results[final_n]
        
        # Create table
        table = Table(title="Sensitivity Analysis Results")
        table.add_column("Variable")
        table.add_column("First Order (S1)")
        table.add_column("Total Order (ST)")
        
        for i, var in enumerate(self.variables):
            table.add_row(
                var.name,
                f"{final_results['S1'][i]:.4f} ± {final_results['S1_conf'][i]:.4f}",
                f"{final_results['ST'][i]:.4f} ± {final_results['ST_conf'][i]:.4f}"
            )
        
        self.console.print("\n")
        self.console.print(table)
        self.console.print("\nOutput files saved in:")
        self.console.print(f"  • {self.output_dir}/")
        self.console.print("\n")











# Example Usage and Documentation
if __name__ == "__main__":
    """
    PyEGRO Sensitivity Analysis Module - Full Documentation and Examples
    =================================================================
    
    This module provides three ways to perform Sobol sensitivity analysis:
    1. Using InitialDesign class (recommended for new projects)
    2. Using data_info.json (for existing PyEGRO projects)
    3. Using trained surrogate models (for evaluating meta-models)
    
    The Borehole function is used as an example throughout this documentation
    as it's a well-known benchmark for uncertainty quantification.
    """
    
    #==========================================================================
    # Borehole Function Definition
    #==========================================================================
    def borehole_function(x):
        """
        Borehole function for water flow rate modeling.
        
        Input Parameters:
        ----------------
        rw : radius of borehole (m)
        r  : radius of influence (m)
        Tu : transmissivity of upper aquifer (m²/yr)
        Hu : potentiometric head of upper aquifer (m)
        Tl : transmissivity of lower aquifer (m²/yr)
        Hl : potentiometric head of lower aquifer (m)
        L  : length of borehole (m)
        Kw : hydraulic conductivity of borehole (m/yr)
        
        Returns:
        --------
        Water flow rate (m³/yr)
        """
        rw, r, Tu, Hu, Tl, Hl, L, Kw = [x[:, i] for i in range(8)]
        
        numerator = 2 * np.pi * Tu * (Hu - Hl)
        denominator = np.log(r / rw) * (1 + (2 * L * Tu) / (np.log(r / rw) * rw**2 * Kw) + Tu/Tl)
        
        return numerator / denominator
    
    #==========================================================================
    # Option 1: Using InitialDesign (Recommended Approach)
    #==========================================================================
    """
    The InitialDesign approach is recommended for new projects as it:
    - Provides a structured way to define variables
    - Handles different variable types (design and environmental)
    - Automatically generates data_info.json
    - Ensures consistency across the PyEGRO workflow
    """
    print("\nOption 1: Using InitialDesign")
    print("=" * 50)
    
    from PyEGRO.doe.initial_design import InitialDesign
    from PyEGRO.sensitivity import SobolAnalyzer
    
    # Step 1: Create InitialDesign instance
    design = InitialDesign(
        objective_function=borehole_function,
        output_dir='DATA_PREPARATION',
        show_progress=True,
        show_result=True
    )
    
    # Step 2: Add Design Variables
    # These are variables that can be controlled in the design process
    design.add_design_variable(
        name='rw',
        range_bounds=[0.05, 0.15],
        cov=0.1,
        description='radius of borehole (m)'
    )
    
    design.add_design_variable(
        name='r',
        range_bounds=[100, 50000],
        cov=0.1,
        description='radius of influence (m)'
    )
    
    # Step 3: Add Environmental Variables
    # These are variables with inherent uncertainty
    design.add_env_variable(
        name='Tu',
        distribution='uniform',
        low=63070,
        high=115600,
        description='transmissivity of upper aquifer (m²/yr)'
    )
    
    design.add_env_variable(
        name='Hu',
        distribution='uniform',
        low=990,
        high=1110,
        description='potentiometric head of upper aquifer (m)'
    )
    
    design.add_env_variable(
        name='Tl',
        distribution='uniform',
        low=63.1,
        high=116,
        description='transmissivity of lower aquifer (m²/yr)'
    )
    
    design.add_env_variable(
        name='Hl',
        distribution='uniform',
        low=700,
        high=820,
        description='potentiometric head of lower aquifer (m)'
    )
    
    design.add_design_variable(
        name='L',
        range_bounds=[1120, 1680],
        cov=0.1,
        description='length of borehole (m)'
    )
    
    design.add_design_variable(
        name='Kw',
        range_bounds=[9855, 12045],
        cov=0.1,
        description='hydraulic conductivity of borehole (m/yr)'
    )
    
    # Step 4: Generate Initial Samples
    design.run(num_samples=50)
    
    # Step 5: Create and Run Sensitivity Analysis
    analyzer1 = SobolAnalyzer.from_initial_design(
        design,
        output_dir='SENSITIVITY_FROM_DESIGN'
    )
    
    # Run analysis with explicit settings
    results1 = analyzer1.run_analysis(
        true_func=borehole_function,
        n_samples=8192,  # Base sample size
        sample_sizes=[256, 512, 1024, 2048, 4096, 8192],  # For convergence study
        calc_second_order=False,  # Only first and total order indices
        seed=42  # For reproducibility
    )
    
    #==========================================================================
    # Option 2: Using data_info.json
    #==========================================================================
    """
    Using data_info.json directly is useful when:
    - Working with existing PyEGRO projects
    - Loading predefined variable configurations
    - Integrating with other PyEGRO modules
    """
    print("\nOption 2: Using data_info.json")
    print("=" * 50)
    
    # Simple setup using existing data_info.json
    analyzer2 = SobolAnalyzer(
        data_info_path='DATA_PREPARATION/data_info.json',
        output_dir='SENSITIVITY_FROM_JSON'
    )
    
    results2 = analyzer2.run_analysis(
        true_func=borehole_function,
        n_samples=8192,
        sample_sizes=[256, 512, 1024, 2048, 4096, 8192],
        calc_second_order=False
    )
    
    #==========================================================================
    # Option 3: Using Surrogate Model
    #==========================================================================
    """
    Using a surrogate model is beneficial when:
    - The true function is computationally expensive
    - You want to analyze the behavior of the meta-model
    - Performing large-scale sensitivity studies
    
    Required files in model_path:
    - gpr_model.pth: Trained GPR model state
    - scaler_X.pkl: Input scaler
    - scaler_y.pkl: Output scaler
    """
    print("\nOption 3: Using Surrogate Model")
    print("=" * 50)
    
    # Initialize analyzer with both model and data info
    analyzer3 = SobolAnalyzer(
        model_path='RESULT_MODEL_GPR',
        data_info_path='DATA_PREPARATION/data_info.json',
        output_dir='SENSITIVITY_FROM_SURROGATE',
        show_progress=True,
        show_result=True
    )
    
    # Run analysis using the surrogate model
    results3 = analyzer3.run_analysis(
        n_samples=8192,
        sample_sizes=[256, 512, 1024, 2048, 4096, 8192],
        calc_second_order=False
    )
    
    #==========================================================================
    # Compare Results (Optional)
    #==========================================================================
    """
    Comparing results between approaches can help:
    - Validate surrogate model accuracy
    - Understand sampling convergence
    - Identify key influential variables
    """
    print("\nComparison of Results")
    print("=" * 50)
    
    # Get final results from largest sample size
    final_n = 8192
    variables = analyzer1.variables
    
    # Create comparison table
    print("\nComparison of First-Order Sensitivity Indices:")
    print("-" * 75)
    print(f"{'Variable':<15} {'True Func':<12} {'Surrogate':<12} {'Difference':<12}")
    print("-" * 75)
    
    for i, var in enumerate(variables):
        s1_true = results1[final_n]['S1'][i]
        s1_surrogate = results3[final_n]['S1'][i]
        diff = abs(s1_true - s1_surrogate)
        
        print(f"{var.name:<15} {s1_true:>10.4f}  {s1_surrogate:>10.4f}  {diff:>10.4f}")
    
    print("\nAnalysis completed!")
    print("Results saved in:")
    print("  - From InitialDesign: SENSITIVITY_FROM_DESIGN/")
    print("  - From data_info.json: SENSITIVITY_FROM_JSON/")
    print("  - From surrogate model: SENSITIVITY_FROM_SURROGATE/")
    
    """
    Generated Output Files:
    ----------------------
    Each output directory contains:
    1. sobol_results.json: Raw sensitivity indices for all sample sizes
    2. sensitivity_indices.csv: Final indices in CSV format
    3. convergence_plot.png: Visualization of convergence behavior
    4. sensitivity_indices.png: Bar plot of final indices
    
    Additional Notes:
    ----------------
    - Sample sizes should be powers of 2 for efficient convergence analysis
    - Base sample size (N) will be multiplied by SALib based on:
        * N*(2D+2) samples if calc_second_order=False
        * N*(2D+2+((D-1)*D)/2) samples if calc_second_order=True
        * Where D is the number of variables
    - Progress bars show real-time analysis progress
    - Results include both first-order (S1) and total-order (ST) indices
    - Confidence intervals are provided for all sensitivity indices
    """