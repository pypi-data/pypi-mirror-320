"""
PyEGRO Robust Optimization Module - Polynomial Chaos Expansion (PCE) Approach
-------------------------------------------------------------------------
This module implements robust optimization using Polynomial Chaos Expansion for
uncertainty quantification in multi-objective optimization problems.
"""

import os
import numpy as np
import pandas as pd
import time
from typing import List, Dict, Optional, Any
import chaospy as cp
from scipy.stats import norm

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.lhs import LHS
from pymoo.indicators.hv import HV

from ..doe.sampling import AdaptiveDistributionSampler
from .visualization import OptimizationVisualizer, ParameterInformationDisplay

class PCESampler:
    """Handles PCE-based sampling for uncertainty quantification."""
    
    def __init__(self, n_samples: int = 200, order: int = 3):
        self.n_samples = n_samples
        self.order = order
        
    def generate_samples(self, mean: float, std: float, bounds: Optional[tuple] = None) -> np.ndarray:
        """Generate PCE samples with improved uncertainty quantification."""
        if bounds is not None:
            # Use truncated normal with adjusted parameters
            a = (bounds[0] - mean) / std
            b = (bounds[1] - mean) / std
            distribution = cp.TruncNormal(mu=mean, sigma=std, lower=bounds[0], upper=bounds[1])
            
            # Apply scaling factor to maintain variance consistency
            samples = distribution.sample(self.n_samples)
            
            # Adjust samples to match theoretical moments
            theoretical_std = std * np.sqrt(1 - (b * norm.pdf(b) - a * norm.pdf(a)) / 
                                         (norm.cdf(b) - norm.cdf(a)) - 
                                         ((norm.pdf(b) - norm.pdf(a)) / 
                                          (norm.cdf(b) - norm.cdf(a)))**2)
            
            # Scale samples to match theoretical standard deviation
            samples = mean + (samples - np.mean(samples)) * (theoretical_std / np.std(samples))
        else:
            # For unbounded normal, use standard normal distribution
            distribution = cp.Normal(mean, std)
            samples = distribution.sample(self.n_samples)
        
        return samples

class RobustOptimizationProblemPCE(Problem):
    """Multi-objective optimization problem using Polynomial Chaos Expansion for uncertainty quantification."""
    
    def __init__(self, 
                 variables: List[Dict], 
                 true_func: Optional[callable] = None,
                 gpr_handler: Optional[Any] = None,
                 num_pce_samples: int = 200, 
                 pce_order: int = 3,
                 batch_size: int = 1000):
        """
        Initialize PCE-based robust optimization problem.
        
        Args:
            variables: List of variable definitions
            true_func: True objective function (if using direct evaluation)
            gpr_handler: Handler for GPR model evaluations (if using surrogate)
            num_pce_samples: Number of PCE samples per evaluation
            pce_order: Order of PCE expansion
            batch_size: Batch size for model evaluations
        """
        if true_func is None and gpr_handler is None:
            raise ValueError("Either true_func or gpr_handler must be provided")
            
        self.true_func = true_func
        self.gpr_handler = gpr_handler
        self.variables = variables
        self.batch_size = batch_size
        self.pce_sampler = PCESampler(n_samples=num_pce_samples, order=pce_order)
        
        # Filter design variables
        self.design_vars = [var for var in variables if var['vars_type'] == 'design_vars']
        if not self.design_vars:
            raise ValueError("No design variables found in problem definition")
        
        # Set optimization bounds
        xl = np.array([var['range'][0] for var in self.design_vars])
        xu = np.array([var['range'][1] for var in self.design_vars])
        
        # Initialize problem
        super().__init__(
            n_var=len(self.design_vars),
            n_obj=2,  # Mean and Std
            n_constr=0,
            xl=xl,
            xu=xu
        )
        
        self.all_evaluations = []
        
    def _generate_samples(self, design_point: np.ndarray) -> np.ndarray:
        """Generate PCE samples for a given design point."""
        samples = np.zeros((self.pce_sampler.n_samples, len(self.variables)))
        
        for i, var in enumerate(self.variables):
            if var['vars_type'] == 'design_vars':
                idx = next(j for j, dv in enumerate(self.design_vars) if dv['name'] == var['name'])
                if var['cov'] > 0:  # Uncertain design variable
                    mean = design_point[idx]
                    std = var['cov'] * abs(mean)
                    samples[:, i] = self.pce_sampler.generate_samples(
                        mean=mean,
                        std=std,
                        bounds=var['range']
                    )
                else:  # Deterministic design variable
                    samples[:, i] = design_point[idx]
            
            elif var['vars_type'] == 'env_vars':
                if var['distribution'] == 'normal':
                    mean = var['mean']
                    std = var['cov'] * abs(mean)
                    samples[:, i] = self.pce_sampler.generate_samples(
                        mean=mean,
                        std=std
                    )
                elif var['distribution'] == 'uniform':
                    low, high = float(var['low']), float(var['high'])
                    distribution = cp.Uniform(low, high)
                    samples[:, i] = distribution.sample(self.pce_sampler.n_samples)
        
        return samples

    def _evaluate_samples(self, samples: np.ndarray) -> np.ndarray:
        """Evaluate samples using either true function or surrogate."""
        if self.true_func is not None:
            return self.true_func(samples)
        else:
            return self.gpr_handler.evaluate_batch(samples, self.batch_size)

    def _evaluate(self, X: np.ndarray, out: Dict, *args, **kwargs):
        """Evaluate objectives with PCE-based uncertainty estimation."""
        n_points = X.shape[0]
        F = np.zeros((n_points, 2))
        
        for i in range(n_points):
            # Generate multiple PCE sample sets for better convergence
            n_repetitions = 5
            responses_all = []
            
            for _ in range(n_repetitions):
                samples = self._generate_samples(X[i])
                responses = self._evaluate_samples(samples)
                responses_all.extend(responses)
            
            # Compute statistics using all samples
            responses_array = np.array(responses_all)
            
            # Use robust statistics
            F[i, 0] = np.median(responses_array)  # More robust than mean
            F[i, 1] = np.percentile(responses_array, 84.13) - np.percentile(responses_array, 15.87)
            F[i, 1] /= 2  # Approximate standard deviation using percentiles
        
        out["F"] = F
        self.all_evaluations.extend(F)

def setup_algorithm(pop_size: int) -> NSGA2:
    """Setup NSGA-II algorithm with standard parameters."""
    return NSGA2(
        pop_size=pop_size,
        sampling=LHS(),
        crossover=SBX(prob=0.9, eta=20),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )

def run_robust_optimization(data_info: Dict,
                          true_func: Optional[callable] = None,
                          gpr_handler: Optional[Any] = None,
                          pce_samples: int = 200,
                          pce_order: int = 3,
                          pop_size: int = 50,
                          n_gen: int = 100,
                          metric: str = 'hv',
                          show_info: bool = True,
                          verbose: bool = False) -> Dict:
    """
    Run robust optimization using PCE for uncertainty quantification.
    
    Args:
        data_info: Problem definition data
        true_func: True objective function (if using direct evaluation)
        gpr_handler: Handler for GPR model evaluations (if using surrogate)
        pce_samples: Number of PCE samples per evaluation
        pce_order: Order of PCE expansion
        pop_size: Population size for NSGA-II
        n_gen: Number of generations
        metric: Performance metric ('hv' for hypervolume)
        show_info: Whether to display variable information
        verbose: Whether to print detailed progress
        
    Returns:
        Dictionary containing optimization results
    """
    if show_info:
        ParameterInformationDisplay.print_variable_information(data_info['variables'])
        print("\nOptimization Configuration:")
        print("-" * 50)
        print(f"Evaluation type: {'Direct Function' if true_func else 'Surrogate Model'}")
        print(f"Population size: {pop_size}")
        print(f"Number of generations: {n_gen}")
        print(f"PCE samples per evaluation: {pce_samples}")
        print(f"PCE order: {pce_order}")
        print(f"Performance metric: {metric.upper()}")
        print("-" * 50 + "\n")
    
    start_time = time.time()
    
    # Setup problem
    problem = RobustOptimizationProblemPCE(
        variables=data_info['variables'],
        true_func=true_func,
        gpr_handler=gpr_handler,
        num_pce_samples=pce_samples,
        pce_order=pce_order
    )
    
    # Setup optimization
    algorithm = setup_algorithm(pop_size)
    
    # Setup metric tracking
    class MetricCallback:
        def __init__(self):
            self.metrics = []
            self.n_evals = []
            self.n_pce_evals = []
            self.indicator = None
            self.last_gen = -1
            
        def __call__(self, algorithm):
            if algorithm.n_gen > self.last_gen and show_info:
                progress = min((algorithm.n_gen + 1) / n_gen * 100, 100)
                elapsed = time.time() - start_time
                if algorithm.n_gen < n_gen:
                    print(f"Progress: {progress:6.1f}% | Generation: {algorithm.n_gen + 1:3d}/{n_gen:3d} | Time: {elapsed:6.1f}s")
                self.last_gen = algorithm.n_gen
            
            F = algorithm.opt.get("F")
            if F is None:
                F = algorithm.pop.get("F")
            
            if self.indicator is None and metric == 'hv':
                ref_point = np.max(F, axis=0) * 1.1
                self.indicator = HV(ref_point=ref_point)
            
            if self.indicator is not None:
                metric_value = self.indicator(F)
                self.metrics.append(metric_value)
                self.n_evals.append(algorithm.evaluator.n_eval)
                self.n_pce_evals.append(algorithm.evaluator.n_eval * pce_samples)
    
    callback = MetricCallback()
    
    # Run optimization
    res = minimize(
        problem,
        algorithm,
        ('n_gen', n_gen),
        callback=callback,
        seed=42,
        verbose=verbose
    )
    
    total_time = time.time() - start_time
    
    # Prepare results
    results = {
        'pareto_front': res.F,
        'pareto_set': res.X,
        'convergence_history': {
            'n_evals': callback.n_evals,
            'n_pce_evals': callback.n_pce_evals,
            'metric_values': callback.metrics,
            'metric_type': metric
        },
        'runtime': total_time,
        'success': True
    }
    
    if show_info:
        print(f"\nOptimization completed in {total_time:.2f} seconds")
        print(f"Number of Pareto solutions: {len(res.F)}")
        print(f"Final {metric.upper()} value: {callback.metrics[-1]:.6f}\n")
    
    return results


def save_optimization_results(results: Dict,
                            data_info: Dict,
                            save_dir: str = 'RESULT_PARETO_FRONT_PCE') -> None:
    """
    Save optimization results and create visualizations.
    
    Args:
        results: Optimization results dictionary
        data_info: Problem definition data
        save_dir: Directory to save results
    """
    os.makedirs(save_dir, exist_ok=True)
    
    # Get design variable names
    design_var_names = [var['name'] for var in data_info['variables'] 
                       if var['vars_type'] == 'design_vars']
    
    # Create results DataFrame
    pareto_df = pd.DataFrame(
        np.hstack([results['pareto_set'], results['pareto_front']]),
        columns=design_var_names + ['Mean', 'StdDev']
    )
    pareto_df.sort_values('StdDev', ascending=True, inplace=True)
    
    # Save numerical results
    pareto_df.to_csv(os.path.join(save_dir, 'pareto_solutions.csv'), index=False)
    
    # Create visualizations
    visualizer = OptimizationVisualizer(save_dir=save_dir)
    visualizer.create_all_visualizations(
        results_df=pareto_df,
        convergence_history=results.get('convergence_history', None)
    )
    
    # Save convergence data if available
    if 'convergence_history' in results:
        history = results['convergence_history']
        convergence_df = pd.DataFrame({
            'evaluations': history['n_evals'],
            'pce_evaluations': history['n_pce_evals'],
            f"{history['metric_type']}_value": history['metric_values']
        })
        convergence_df.to_csv(os.path.join(save_dir, 'convergence.csv'), 
                            index=False)
        
        # Save optimization summary
        with open(os.path.join(save_dir, 'optimization_summary.txt'), 'w') as f:
            # General Information
            f.write("Optimization Results Summary\n")
            f.write("=" * 50 + "\n\n")
            
            # Problem Information
            f.write("Problem Information:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Number of design variables: {len(design_var_names)}\n")
            f.write(f"Number of objectives: 2 (Mean, StdDev)\n\n")
            
            # Variable Information
            f.write("Variable Information:\n")
            f.write("-" * 20 + "\n")
            
            # Design Variables
            f.write("\nDesign Variables:\n")
            for var in data_info['variables']:
                if var['vars_type'] == 'design_vars':
                    f.write(f"\n{var['name']}:\n")
                    f.write(f"  Type: {var['vars_type']}\n")
                    f.write(f"  Distribution: {var.get('distribution', 'Normal')}\n")
                    f.write(f"  Range: [{var['range'][0]:.3f}, {var['range'][1]:.3f}]\n")
                    f.write(f"  CoV: {var.get('cov', 0):.3f}\n")
            
            # Environmental Variables
            f.write("\nEnvironmental Variables:\n")
            for var in data_info['variables']:
                if var['vars_type'] == 'env_vars':
                    f.write(f"\n{var['name']}:\n")
                    f.write(f"  Type: {var['vars_type']}\n")
                    f.write(f"  Distribution: {var['distribution']}\n")
                    if var['distribution'] == 'uniform':
                        f.write(f"  Range: [{var['low']:.3f}, {var['high']:.3f}]\n")
                    else:
                        f.write(f"  Mean: {var['mean']:.3f}\n")
                        f.write(f"  CoV: {var['cov']:.3f}\n")
            
            # Results Summary
            f.write("\nResults Summary:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Runtime: {results['runtime']:.2f} seconds\n")
            f.write(f"Number of Pareto solutions: {len(pareto_df)}\n")
            
            # Metric Information
            f.write(f"\nMetric Information ({history['metric_type'].upper()}):\n")
            f.write(f"Initial value: {history['metric_values'][0]:.6f}\n")
            f.write(f"Final value: {history['metric_values'][-1]:.6f}\n")
            improvement = ((history['metric_values'][-1] / history['metric_values'][0]) - 1) * 100
            f.write(f"Improvement: {improvement:.1f}%\n")
            
            # Evaluations
            f.write(f"\nEvaluations:\n")
            f.write(f"Total design evaluations: {history['n_evals'][-1]:,}\n")
            f.write(f"Total PCE evaluations: {history['n_pce_evals'][-1]:,}\n")
            
            # Objective Ranges
            f.write("\nObjective Ranges:\n")
            f.write("Mean Performance:\n")
            f.write(f"  Min: {pareto_df['Mean'].min():.4f}\n")
            f.write(f"  Max: {pareto_df['Mean'].max():.4f}\n")
            f.write("Standard Deviation:\n")
            f.write(f"  Min: {pareto_df['StdDev'].min():.4f}\n")
            f.write(f"  Max: {pareto_df['StdDev'].max():.4f}\n")


if __name__ == "__main__":
    """
    PyEGRO Robust Optimization Module - PCE Example
    =============================================
    
    This example demonstrates three ways to perform robust optimization using PCE:
    1. Using InitialDesign with direct function evaluation
    2. Using data_info.json with existing setup
    3. Using trained surrogate models
    
    The Borehole function is used as an example throughout this documentation.
    """
    
    import numpy as np
    from PyEGRO.doe.initial_design import InitialDesign
    from PyEGRO.meta.meta_trainer import MetaTraining
    from PyEGRO.meta.gpr_utils import DeviceAgnosticGPR
    import json
    
    def borehole_function(x):
        """Borehole function for water flow rate modeling."""
        rw, r, Tu, Hu, Tl, Hl, L, Kw = [x[:, i] for i in range(8)]
        
        numerator = 2 * np.pi * Tu * (Hu - Hl)
        denominator = np.log(r / rw) * (1 + (2 * L * Tu) / (np.log(r / rw) * rw**2 * Kw) + Tu/Tl)
        
        return numerator / denominator
    
    #==========================================================================
    # Option 1: Direct Function Evaluation
    #==========================================================================
    print("\nOption 1: Direct Function Evaluation")
    print("=" * 50)
    
    # Create initial design
    design = InitialDesign(
        objective_function=borehole_function,
        output_dir='DATA_PREPARATION'
    )
    
    # Add variables
    design.add_design_variable(
        name='rw', range_bounds=[0.05, 0.15], cov=0.1,
        description='radius of borehole (m)'
    )
    design.add_design_variable(
        name='r', range_bounds=[100, 50000], cov=0.1,
        description='radius of influence (m)'
    )
    design.add_env_variable(
        name='Tu', distribution='uniform',
        low=63070, high=115600,
        description='transmissivity of upper aquifer (m²/yr)'
    )
    design.add_env_variable(
        name='Hu', distribution='uniform',
        low=990, high=1110,
        description='potentiometric head of upper aquifer (m)'
    )
    design.add_env_variable(
        name='Tl', distribution='uniform',
        low=63.1, high=116,
        description='transmissivity of lower aquifer (m²/yr)'
    )
    design.add_env_variable(
        name='Hl', distribution='uniform',
        low=700, high=820,
        description='potentiometric head of lower aquifer (m)'
    )
    design.add_design_variable(
        name='L', range_bounds=[1120, 1680], cov=0.1,
        description='length of borehole (m)'
    )
    design.add_design_variable(
        name='Kw', range_bounds=[9855, 12045], cov=0.1,
        description='hydraulic conductivity of borehole (m/yr)'
    )
    
    # Run optimization
    results1 = run_robust_optimization(
        data_info=design.data_info,
        true_func=borehole_function,
        pce_samples=500,
        pce_order=4,
        pop_size=50,
        n_gen=100
    )
    
    save_optimization_results(
        results=results1,
        data_info=design.data_info,
        save_dir='RESULT_PCE_DIRECT'
    )
    
    #==========================================================================
    # Option 2: Using data_info.json
    #==========================================================================
    print("\nOption 2: Using data_info.json")
    print("=" * 50)
    
    with open('DATA_PREPARATION/data_info.json', 'r') as f:
        data_info = json.load(f)
    
    results2 = run_robust_optimization(
        data_info=data_info,
        true_func=borehole_function,
        pce_samples=500,
        pce_order=4,
        pop_size=50,
        n_gen=100
    )
    
    save_optimization_results(
        results=results2,
        data_info=data_info,
        save_dir='RESULT_PCE_JSON'
    )
    
    #==========================================================================
    # Option 3: Using Surrogate Model
    #==========================================================================
    print("\nOption 3: Using Surrogate Model")
    print("=" * 50)
    
    # Load existing problem definition
    with open('DATA_PREPARATION/data_info.json', 'r') as f:
        data_info = json.load(f)

    # Initialize GPR handler (**GPR need to be trained)
    gpr_handler = DeviceAgnosticGPR(prefer_gpu=True)
    gpr_handler.load_model('RESULT_MODEL_GPR')
    
    # Run optimization with surrogate
    results3 = run_robust_optimization(
        gpr_handler=gpr_handler,
        data_info=data_info,
        pce_samples=500,
        pce_order=4,
        pop_size=50,
        n_gen=100
    )
    
    save_optimization_results(
        results=results3,
        data_info=data_info
    )
    

  