

"""
Uncertainty Quantification Module for PyEGRO using Monte Carlo Simulation.
"""

import numpy as np
import pickle
import pandas as pd
import os
import json
import joblib
from pyDOE import lhs
import torch
import gpytorch
from ..doe.sampling import AdaptiveDistributionSampler
from typing import List, Dict, Any, Optional
from pathlib import Path
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from matplotlib import rcParams 
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn, TaskProgressColumn

# Setting plots - Front
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 14
rcParams['axes.titlesize'] = 16
rcParams['axes.labelsize'] = 14
rcParams['xtick.labelsize'] = 14
rcParams['ytick.labelsize'] = 14

# Suppress warning GP
import warnings
from gpytorch.utils.warnings import GPInputWarning
warnings.filterwarnings("ignore", category=GPInputWarning)

from ..doe.initial_design import InitialDesign

class GPRegressionModel(gpytorch.models.ExactGP):
    """Gaussian Process Regression Model."""
    
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

        # Initial Hyperparameters - keep standard settings
        self.covar_module.base_kernel.lengthscale = 1.0  
        self.covar_module.outputscale = 1.0  
        self.likelihood.noise_covar.noise = 1e-4  

    def forward(self, x: torch.Tensor) -> gpytorch.distributions.MultivariateNormal:
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)


class DeviceAgnosticGPR:
    """GPR model handler with device management."""
    
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

    def load_model(self, model_dir: str = 'RESULT_MODEL_GPR'):
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
            
            # Move to device
            self.model = self.model.to(self.device)
            self.model.likelihood = self.model.likelihood.to(self.device)
            
            # Set evaluation mode
            self.model.eval()
            self.model.likelihood.eval()
            
            print(f"Model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

    def evaluate_batch(self, X: np.ndarray, batch_size: int = 1000) -> np.ndarray:
        """Evaluate model predictions in batches."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model first.")
            
        n_samples = X.shape[0]
        predictions = np.zeros(n_samples)
        X_scaled = self.scaler_X.transform(X)
        
        batch_iterator = range(0, n_samples, batch_size)
        
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            with gpytorch.settings.fast_pred_var(), \
                gpytorch.settings.cholesky_jitter(1e-3), \
                gpytorch.settings.max_cholesky_size(2000):
                
                for i in batch_iterator:
                    end_idx = min(i + batch_size, n_samples)
                    X_batch = torch.tensor(X_scaled[i:end_idx], dtype=torch.float32).to(self.device)
                    
                    with torch.no_grad():
                        try:
                            output = self.model(X_batch)
                            pred_batch = output.mean.cpu().numpy()
                        except RuntimeError:
                            with gpytorch.settings.cholesky_jitter(1e-1):
                                output = self.model(X_batch)
                                pred_batch = output.mean.cpu().numpy()
                    
                    pred_batch = self.scaler_y.inverse_transform(pred_batch.reshape(-1, 1)).flatten()
                    predictions[i:end_idx] = pred_batch
                        
        return predictions


class InformationVisualization:
    """Handles visualization of uncertainty analysis results."""
    
    def __init__(self):
        self.output_dir = Path('RESULT_QOI')
        self.output_dir.mkdir(exist_ok=True)

    def create_visualization(self, results_df: pd.DataFrame, design_vars: List[Dict[str, Any]]):
        """Create appropriate visualization based on number of design variables."""
        plt.close('all')
        
        n_design_vars = len(design_vars)
        
        if n_design_vars == 1:
            fig = self._create_1d_visualization(results_df, design_vars)
        elif n_design_vars == 2:
            fig = self._create_2d_visualization(results_df, design_vars)
        else:
            fig = self._create_correlation_matrix(results_df, design_vars)

        self._save_visualizations(fig)

    def _create_1d_visualization(self, results_df: pd.DataFrame, design_vars: List[Dict[str, Any]]):
        """Create 1D visualization with uncertainty bounds."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), height_ratios=[2, 2])
        
        sorted_data = results_df.sort_values(by=design_vars[0]['name'])
        x_var = design_vars[0]['name']
        
        # Mean with uncertainty bounds
        ax1.plot(sorted_data[x_var], sorted_data['Mean'],
                color='blue', label='Mean Response', linewidth=1.5)
        
        upper_bound = sorted_data['Mean'] + 2*sorted_data['StdDev']
        lower_bound = sorted_data['Mean'] - 2*sorted_data['StdDev']
        
        ax1.fill_between(sorted_data[x_var],
                        lower_bound,
                        upper_bound,
                        alpha=0.2, color='blue',
                        label='Mean ± 2σ')
        
        ax1.set_xlabel(x_var)
        ax1.set_ylabel('Mean Response')
        ax1.set_title('Mean Response with Uncertainty Bounds')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Standard Deviation
        ax2.plot(sorted_data[x_var], sorted_data['StdDev'],
                color='red', label='Standard Deviation', linewidth=1.5)
        
        ax2.set_xlabel(x_var)
        ax2.set_ylabel('Standard Deviation')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        return fig

    def _create_2d_visualization(self, results_df: pd.DataFrame, design_vars: List[Dict[str, Any]]):
        """Create 2D visualization with surface plots."""
        fig = plt.figure(figsize=(15, 6))
        plt.subplots_adjust(wspace=0.4)
        
        x = results_df[design_vars[0]['name']]
        y = results_df[design_vars[1]['name']]
        z_mean = results_df['Mean']
        z_std = results_df['StdDev']
        
        x_unique = np.linspace(x.min(), x.max(), 100)
        y_unique = np.linspace(y.min(), y.max(), 100)
        x_grid, y_grid = np.meshgrid(x_unique, y_unique)
        
        z_mean_grid = griddata((x, y), z_mean, (x_grid, y_grid), method='cubic')
        z_std_grid = griddata((x, y), z_std, (x_grid, y_grid), method='cubic')
        
        ax1 = fig.add_subplot(121, projection='3d')
        surf1 = ax1.plot_surface(x_grid, y_grid, z_mean_grid, 
                               cmap='viridis',
                               alpha=1,
                               antialiased=True)
        
        self._format_3d_subplot(ax1, design_vars[0]['name'], design_vars[1]['name'], 
                              'Mean Response', surf1, 'Mean Value', 'Mean Response Surface')
        
        ax2 = fig.add_subplot(122, projection='3d')
        surf2 = ax2.plot_surface(x_grid, y_grid, z_std_grid,
                               cmap='plasma',
                               alpha=1,
                               antialiased=True)
        
        self._format_3d_subplot(ax2, design_vars[0]['name'], design_vars[1]['name'], 
                              'Std Dev', surf2, 'Standard Deviation Value', 
                              'Standard Deviation Surface')
        
        return fig

    def _format_3d_subplot(self, ax, xlabel, ylabel, zlabel, surf, colorbar_label, title):
        """Format 3D subplots."""
        ax.set_xlabel(xlabel, labelpad=10)
        ax.set_ylabel(ylabel, labelpad=10)
        ax.set_zlabel(zlabel, labelpad=10)
        ax.view_init(elev=20, azim=45)
        ax.grid(True, alpha=0.3)
        
        cbar = plt.colorbar(surf, ax=ax, pad=0.1)
        cbar.set_label(colorbar_label)
        ax.set_title(title, pad=20)

    def _create_correlation_matrix(self, results_df: pd.DataFrame, design_vars: List[Dict[str, Any]]):
        """Create correlation matrix visualization."""
        fig = plt.figure(figsize=(10, 8))
        correlation_data = results_df[[var['name'] for var in design_vars] + ['Mean', 'StdDev']].corr()
        plt.imshow(correlation_data, cmap='RdBu', aspect='auto')
        plt.colorbar(label='Correlation Coefficient')
        plt.xticks(range(len(correlation_data.columns)), correlation_data.columns, rotation=45)
        plt.yticks(range(len(correlation_data.columns)), correlation_data.columns)
        plt.title('Correlation Matrix of Design Variables and Response')
        return fig

    def _save_visualizations(self, fig):
        """Save visualizations."""
        plt.savefig(self.output_dir / 'uncertainty_analysis.png',
                   dpi=300, 
                   bbox_inches='tight',
                   pad_inches=0.05)
        
        with open(self.output_dir / 'uncertainty_analysis.fig.pkl', 'wb') as fig_file:
            pickle.dump(fig, fig_file)
        
        plt.close(fig)


class UncertaintyPropagation:
    """Main class for uncertainty propagation analysis."""
    
    def __init__(self, 
                 data_info_path: str = "DATA_PREPARATION/data_info.json",
                 true_func: Optional[callable] = None,
                 model_path: Optional[str] = None,
                 use_gpu: bool = True,
                 output_dir: str = "RESULT_QOI",
                 show_variables_info: bool = True,
                 random_seed: int = 42):
        """Initialize UncertaintyPropagation.
        
        Args:
            data_info_path: Path to the data configuration file
            true_func: True objective function (if using direct evaluation)
            model_path: Path to trained GPR model (if using surrogate)
            use_gpu: Whether to use GPU if available for surrogate model
            output_dir: Directory for saving results
            show_variables_info: Whether to display variable information
            random_seed: Random seed for reproducibility
        """
        if true_func is None and model_path is None:
            raise ValueError("Either true_func or model_path must be provided")
            
        np.random.seed(random_seed)
        torch.manual_seed(random_seed)
        
        # Load data info
        with open(data_info_path, 'r') as f:
            data_info = json.load(f)
        self.variables = data_info['variables']
        
        # Set evaluation function and display settings
        self.true_func = true_func
        self.use_surrogate = true_func is None
        self.show_variables_info = show_variables_info
        
        # Initialize surrogate model if needed
        if self.use_surrogate:
            self.gpr_handler = DeviceAgnosticGPR(prefer_gpu=use_gpu)
            if not self.gpr_handler.load_model(model_path):
                raise RuntimeError("Failed to load GPR model")
        else:
            self.gpr_handler = None
            
        # Initialize tools
        self.sampler = AdaptiveDistributionSampler()
        self.visualizer = InformationVisualization()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Display variable information if enabled
        if self.show_variables_info:
            self.display_variable_info()

    def display_variable_info(self):
        """Display detailed information about all variables."""
        print("\nVariable Information Summary:")
        print("=" * 80)
        
        design_vars = []
        env_vars = []
        
        for var in self.variables:
            if var['vars_type'] == 'design_vars':
                design_vars.append(var)
            else:
                env_vars.append(var)
        
        # Display Design Variables
        if design_vars:
            print("\nDesign Variables:")
            print("-" * 40)
            for var in design_vars:
                print(f"\nName: {var['name']}")
                print(f"Description: {var.get('description', 'Not provided')}")
                print(f"Range: [{var['range'][0]}, {var['range'][1]}]")
                print(f"Coefficient of Variation (CoV): {var.get('cov', 0)}")
                if var.get('cov', 0) > 0:
                    print("Type: Uncertain")
                    print("Distribution: Normal")  # Design variables use normal distribution by default
                else:
                    print("Type: Deterministic")
                    print("Distribution: None")
        
        # Display Environmental Variables
        if env_vars:
            print("\nEnvironmental Variables:")
            print("-" * 40)
            for var in env_vars:
                print(f"\nName: {var['name']}")
                print(f"Description: {var.get('description', 'Not provided')}")
                print(f"Distribution: {var['distribution']}")
                if var['distribution'] == 'uniform':
                    print(f"Range: [{var['low']}, {var['high']}]")
                elif var['distribution'] == 'normal':
                    print(f"Mean: {var['mean']}")
                    print(f"Standard Deviation: {var['std']}")
        
        print("\n" + "=" * 80)

    @classmethod
    def from_initial_design(cls, 
                          design: 'InitialDesign',
                          output_dir: str = "RESULT_QOI",
                          use_gpu: bool = True,
                          random_seed: int = 42) -> 'UncertaintyPropagation':
        """
        Create UncertaintyPropagation instance from InitialDesign.
        
        Args:
            design: InitialDesign instance
            output_dir: Directory for saving results
            use_gpu: Whether to use GPU if available
            random_seed: Random seed for reproducibility
            
        Returns:
            UncertaintyPropagation instance
        """
        return cls(
            data_info_path=os.path.join(design.output_dir, "data_info.json"),
            true_func=design.objective_function,  # Use the true function
            output_dir=output_dir,
            random_seed=random_seed
        )

    def _evaluate_samples(self, X_samples: np.ndarray) -> np.ndarray:
        """Evaluate samples using either true function or surrogate."""
        if self.use_surrogate:
            return self.gpr_handler.evaluate_batch(X_samples)
        else:
            return self.true_func(X_samples)

    def _process_design_point(self, 
                            design_point: np.ndarray, 
                            num_mcs_samples: int) -> np.ndarray:
        """Process a single design point with Monte Carlo sampling."""
        X_samples = np.zeros((num_mcs_samples, len(self.variables)))
        design_var_idx = 0
        
        for i, var in enumerate(self.variables):
            if var['vars_type'] == 'design_vars':
                base_value = design_point[design_var_idx]
                
                if var['cov'] > 0:  # Uncertain design variable
                    lower, upper = var['range']
                    X_samples[:, i] = self.sampler.generate_samples(
                        distribution=var['distribution'],
                        mean=base_value,
                        cov=var['cov'],
                        lower=lower,
                        upper=upper,
                        size=num_mcs_samples
                    )
                else:  # Deterministic design variable
                    X_samples[:, i] = base_value
                
                design_var_idx += 1
                
            else:  # Environmental variable
                X_samples[:, i] = self.sampler.generate_env_samples(var, num_mcs_samples)
        
        Y_samples = self._evaluate_samples(X_samples)
        
        stats = {
            'mean': np.mean(Y_samples),
            'std': np.std(Y_samples),
            'percentiles': np.percentile(Y_samples, [2.5, 97.5])
        }
        
        return np.concatenate((
            design_point,
            [stats['mean'], stats['std'], stats['percentiles'][0], stats['percentiles'][1]]
        ))

    def run_analysis(self,
                    num_design_samples: int = 1000,
                    num_mcs_samples: int = 100000,
                    show_progress: bool = True) -> pd.DataFrame:
        """
        Run the uncertainty propagation analysis.
        
        Args:
            num_design_samples: Number of design points to evaluate
            num_mcs_samples: Number of Monte Carlo samples per design point
            show_progress: Whether to show progress bar
            
        Returns:
            DataFrame containing the analysis results
        """
        if self.show_variables_info:
            print("\nAnalysis Configuration:")
            print(f"Number of design samples: {num_design_samples}")
            print(f"Number of Monte Carlo samples per design point: {num_mcs_samples}")
            print(f"Using surrogate model: {self.use_surrogate}")
            print("\nStarting analysis...\n")
        
        # Get design variables
        design_vars = [var for var in self.variables if var['vars_type'] == 'design_vars']
        design_bounds = np.array([var['range'] for var in design_vars])
        
        # Generate LHS samples for design variables
        lhs_design = lhs(len(design_vars), samples=num_design_samples)
        lhs_design = lhs_design * (design_bounds[:, 1] - design_bounds[:, 0]) + design_bounds[:, 0]
        
        # Process samples
        results = []
        if show_progress:
            with Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(
                    f"[green]Processing {num_design_samples} design points...", 
                    total=num_design_samples
                )
                
                for i in range(num_design_samples):
                    result = self._process_design_point(
                        lhs_design[i],
                        num_mcs_samples
                    )
                    results.append(result)
                    progress.advance(task)
        else:
            for i in range(num_design_samples):
                result = self._process_design_point(
                    lhs_design[i],
                    num_mcs_samples
                )
                results.append(result)
        
        # Create results DataFrame
        columns = ([var['name'] for var in design_vars] +
                  ['Mean', 'StdDev', 'CI_Lower', 'CI_Upper'])
        results_df = pd.DataFrame(results, columns=columns)
        
        # Save results and create visualizations
        self._save_results(results_df)
        
        if self.show_variables_info:
            print("\nAnalysis completed!")
            print(f"Results saved in: {self.output_dir}")
        
        return results_df
    
    def _save_results(self, results_df: pd.DataFrame):
        """Save analysis results and create visualizations."""
        # Save CSV
        results_df.to_csv(self.output_dir / 'uncertainty_propagation_results.csv', index=False)
        
        # Create visualizations
        design_vars = [var for var in self.variables if var['vars_type'] == 'design_vars']
        self.visualizer.create_visualization(results_df, design_vars)
        
        # Save summary statistics
        summary_stats = {
            'mean_range': [float(results_df['Mean'].min()), float(results_df['Mean'].max())],
            'stddev_range': [float(results_df['StdDev'].min()), float(results_df['StdDev'].max())],
            'ci_width_range': [
                float((results_df['CI_Upper'] - results_df['CI_Lower']).min()),
                float((results_df['CI_Upper'] - results_df['CI_Lower']).max())
            ]
        }
        
        with open(self.output_dir / 'analysis_summary.json', 'w') as f:
            json.dump(summary_stats, f, indent=4)


def run_uncertainty_analysis(
    data_info_path: str = "DATA_PREPARATION/data_info.json",
    true_func: Optional[callable] = None,
    model_path: Optional[str] = None,
    num_design_samples: int = 1000,
    num_mcs_samples: int = 100000,
    use_gpu: bool = True,
    output_dir: str = "RESULT_QOI",
    random_seed: int = 42,
    show_progress: bool = True
) -> pd.DataFrame:
    """
    Convenience function to run uncertainty propagation analysis.
    
    Args:
        data_info_path: Path to the data configuration file
        true_func: True objective function (if using direct evaluation)
        model_path: Path to trained GPR model (if using surrogate)
        num_design_samples: Number of design points to evaluate
        num_mcs_samples: Number of Monte Carlo samples per design point
        use_gpu: Whether to use GPU if available for surrogate model
        output_dir: Directory for saving results
        random_seed: Random seed for reproducibility
        show_progress: Whether to show progress bar
        
    Returns:
        DataFrame containing the analysis results
    """
    propagation = UncertaintyPropagation(
        data_info_path=data_info_path,
        true_func=true_func,
        model_path=model_path,
        use_gpu=use_gpu,
        output_dir=output_dir,
        random_seed=random_seed
    )
    
    return propagation.run_analysis(
        num_design_samples=num_design_samples,
        num_mcs_samples=num_mcs_samples,
        show_progress=show_progress
    )






if __name__ == "__main__":
    """
    PyEGRO Uncertainty Propagation Module - Full Documentation and Examples
    ====================================================================
    
    This module provides three ways to perform uncertainty propagation analysis:
    1. Using InitialDesign class (recommended for new projects)
    2. Using data_info.json (for existing PyEGRO projects)
    3. Using trained surrogate models (for evaluating meta-models)
    
    The Borehole function is used as an example throughout this documentation
    as it's a well-known benchmark for uncertainty quantification.
    """
    
    #==========================================================================
    # Borehole Function Definition
    #==========================================================================
    import numpy as np
    
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
    # Option 1: Using InitialDesign 
    #==========================================================================
    print("\nOption 1: Using InitialDesign")
    print("=" * 50)
    
    from PyEGRO.doe.initial_design import InitialDesign
    from PyEGRO.uq.mcs import UncertaintyPropagation
    
    # Step 1: Create InitialDesign instance
    design = InitialDesign(
        objective_function=borehole_function,
        output_dir='DATA_PREPARATION',
        show_progress=True,
        show_result=True
    )
    
    # Step 2: Add Design Variables
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
    
    # Step 5: Create and Run Uncertainty Analysis with variable info display
    propagation1 = UncertaintyPropagation.from_initial_design(
        design,
        output_dir='UQ_FROM_DESIGN',
        show_variables_info=True,
        random_seed=42
    )
    
    results1 = propagation1.run_analysis(
        num_design_samples=2000,
        num_mcs_samples=100000,
        show_progress=True
    )
    
    #==========================================================================
    # Option 2: Using data_info.json
    #==========================================================================
    print("\nOption 2: Using data_info.json")
    print("=" * 50)
    
    propagation2 = UncertaintyPropagation(
        data_info_path='DATA_PREPARATION/data_info.json',
        true_func=borehole_function,
        output_dir='UQ_FROM_JSON',
        show_variables_info=True,
        random_seed=42
    )
    
    results2 = propagation2.run_analysis(
        num_design_samples=2000,
        num_mcs_samples=100000,
        show_progress=True
    )
    
    #==========================================================================
    # Option 3: Using Surrogate Model
    #==========================================================================
    print("\nOption 3: Using Surrogate Model")
    print("=" * 50)
    
    # Initialize propagation with surrogate model
    propagation3 = UncertaintyPropagation(
        data_info_path='DATA_PREPARATION/data_info.json',
        model_path='RESULT_MODEL_GPR',
        output_dir='UQ_FROM_SURROGATE',
        show_variables_info=True,
        use_gpu=True
    )
    
    results3 = propagation3.run_analysis(
        num_design_samples=2000,
        num_mcs_samples=100000,
        show_progress=True
    )
    
    #==========================================================================
    # Compare Results
    #==========================================================================
    print("\nComparison of Results")
    print("=" * 50)
    
    print("\nMean Response Ranges:")
    print(f"Direct Method:   [{results1['Mean'].min():.2f}, {results1['Mean'].max():.2f}]")
    print(f"JSON Method:     [{results2['Mean'].min():.2f}, {results2['Mean'].max():.2f}]")
    print(f"Surrogate Model: [{results3['Mean'].min():.2f}, {results3['Mean'].max():.2f}]")
    
    print("\nStandard Deviation Ranges:")
    print(f"Direct Method:   [{results1['StdDev'].min():.2f}, {results1['StdDev'].max():.2f}]")
    print(f"JSON Method:     [{results2['StdDev'].min():.2f}, {results2['StdDev'].max():.2f}]")
    print(f"Surrogate Model: [{results3['StdDev'].min():.2f}, {results3['StdDev'].max():.2f}]")
    
    print("\nAnalysis completed!")
    print("Results saved in:")
    print("  - From InitialDesign: UQ_FROM_DESIGN/")
    print("  - From data_info.json: UQ_FROM_JSON/")
    print("  - From surrogate model: UQ_FROM_SURROGATE/")