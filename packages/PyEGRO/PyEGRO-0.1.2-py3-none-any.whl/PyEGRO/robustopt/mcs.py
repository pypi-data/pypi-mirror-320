"""
PyEGRO Robust Optimization Module - Monte Carlo Simulation (MCS) Approach
-----------------------------------------------------------------------
This module implements robust optimization using Monte Carlo Simulation for
uncertainty quantification in multi-objective optimization problems.
"""

import os
import numpy as np
import pandas as pd
import time
from typing import List, Dict, Optional, Any

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.lhs import LHS
from pymoo.indicators.hv import HV

from ..doe.sampling import AdaptiveDistributionSampler
from .visualization import OptimizationVisualizer, ParameterInformationDisplay

class RobustOptimizationProblemMCS(Problem):
    """Multi-objective optimization problem using Monte Carlo Sampling for uncertainty quantification."""
    
    def __init__(self, 
                 variables: List[Dict], 
                 true_func: Optional[callable] = None,
                 gpr_handler: Optional[Any] = None,
                 num_mcs_samples: int = 100000, 
                 batch_size: int = 1000):
        """
        Initialize the robust optimization problem.

        Args:
            variables: List of variable definitions
            true_func: True objective function (if using direct evaluation)
            gpr_handler: Handler for GPR model evaluations (if using surrogate)
            num_mcs_samples: Number of Monte Carlo samples per evaluation
            batch_size: Batch size for model evaluations
        """
        if true_func is None and gpr_handler is None:
            raise ValueError("Either true_func or gpr_handler must be provided")
            
        self.true_func = true_func
        self.gpr_handler = gpr_handler
        self.variables = variables
        self.n_samples = num_mcs_samples
        self.batch_size = batch_size
        self.dist_sampler = AdaptiveDistributionSampler()
        
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

    def _evaluate_samples(self, samples: np.ndarray) -> np.ndarray:
        """Evaluate samples using either true function or surrogate."""
        if self.true_func is not None:
            return self.true_func(samples)
        else:
            return self.gpr_handler.evaluate_batch(samples, self.batch_size)
            
    def _generate_samples(self, design_point: np.ndarray) -> np.ndarray:
        """Generate MCS samples for a given design point."""
        X_samples = np.zeros((self.n_samples, len(self.variables)))
        design_var_idx = 0
        
        for i, var in enumerate(self.variables):
            if var['vars_type'] == 'design_vars':
                base_value = design_point[design_var_idx]
                
                if var['cov'] > 0:  # Uncertain design variable
                    lower, upper = var['range']
                    X_samples[:, i] = self.dist_sampler.generate_samples(
                        distribution=var['distribution'],
                        mean=base_value,
                        cov=var['cov'],
                        lower=lower,
                        upper=upper,
                        size=self.n_samples
                    )
                else:  # Deterministic design variable
                    X_samples[:, i] = base_value
                
                design_var_idx += 1
                
            else:  # Environmental variable
                X_samples[:, i] = self.dist_sampler.generate_env_samples(var, self.n_samples)
        
        return X_samples

    def _evaluate(self, X: np.ndarray, out: Dict, *args, **kwargs):
        """Evaluate objectives using MCS."""
        n_points = X.shape[0]
        F = np.zeros((n_points, 2))
        
        for i in range(n_points):
            # Generate MCS samples for current design point
            samples = self._generate_samples(X[i])
            
            # Evaluate samples
            responses = self._evaluate_samples(samples)
            
            # Compute statistics
            F[i, 0] = np.mean(responses)  # Mean performance
            F[i, 1] = np.std(responses)   # Standard deviation
        
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
                          mcs_samples: int = 10000,
                          pop_size: int = 50,
                          n_gen: int = 100,
                          metric: str = 'hv',
                          show_info: bool = True,
                          verbose: bool = False) -> Dict:
    """
    Run robust optimization using MCS for uncertainty quantification.
    
    Args:
        data_info: Problem definition data
        true_func: True objective function (if using direct evaluation)
        gpr_handler: Handler for GPR model evaluations (if using surrogate)
        mcs_samples: Number of Monte Carlo samples per evaluation
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
        print(f"MCS samples per evaluation: {mcs_samples}")
        print(f"Performance metric: {metric.upper()}")
        print("-" * 50 + "\n")
    
    start_time = time.time()
    
    # Setup problem
    problem = RobustOptimizationProblemMCS(
        variables=data_info['variables'],
        true_func=true_func,
        gpr_handler=gpr_handler,
        num_mcs_samples=mcs_samples
    )
    
    # Setup optimization
    algorithm = setup_algorithm(pop_size)
    
    # Setup metric tracking
    class MetricCallback:
        def __init__(self):
            self.metrics = []
            self.n_evals = []
            self.indicator = None
            self.last_gen = -1
            
        def __call__(self, algorithm):
            if algorithm.n_gen > self.last_gen and show_info:
                # Fix progress calculation to max at 100%
                progress = min((algorithm.n_gen + 1) / n_gen * 100, 100)
                elapsed = time.time() - start_time
                if algorithm.n_gen < n_gen:  # Only show progress for generations within limit
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
                            save_dir: str = 'RESULT_PARETO_FRONT_MCS') -> None:
    """
    Save optimization results and create visualizations.
    
    Args:
        results: Optimization results dictionary containing:
            - pareto_front: Array of objective values
            - pareto_set: Array of decision variables
            - convergence_history: Dictionary with metric history
            - runtime: Total optimization time
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
            f"{history['metric_type']}_value": history['metric_values']
        })
        convergence_df.to_csv(os.path.join(save_dir, 'convergence.csv'), 
                            index=False)
        
        # Save detailed optimization summary
        with open(os.path.join(save_dir, 'optimization_summary.txt'), 'w') as f:
            f.write("Optimization Results Summary\n")
            f.write("=" * 50 + "\n\n")
            
            # Problem Information
            f.write("Problem Information:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Number of design variables: {len(design_var_names)}\n")
            f.write(f"Number of objectives: 2 (Mean, StdDev)\n\n")
            
            # Optimization Settings
            f.write("Optimization Settings:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Performance metric: {history['metric_type'].upper()}\n")
            f.write(f"Total evaluations: {history['n_evals'][-1]:,}\n\n")
            
            # Results Summary
            f.write("Results Summary:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Runtime: {results['runtime']:.2f} seconds\n")
            f.write(f"Number of Pareto solutions: {len(pareto_df)}\n")
            f.write(f"Initial {history['metric_type'].upper()} value: {history['metric_values'][0]:.6f}\n")
            f.write(f"Final {history['metric_type'].upper()} value: {history['metric_values'][-1]:.6f}\n")
            improvement = ((history['metric_values'][-1] / history['metric_values'][0]) - 1) * 100
            f.write(f"Improvement: {improvement:.1f}%\n\n")
            
            # Objective Ranges
            f.write("Objective Ranges:\n")
            f.write("-" * 20 + "\n")
            f.write("Mean Performance:\n")
            f.write(f"  Min: {pareto_df['Mean'].min():.4f}\n")
            f.write(f"  Max: {pareto_df['Mean'].max():.4f}\n")
            f.write("Standard Deviation:\n")
            f.write(f"  Min: {pareto_df['StdDev'].min():.4f}\n")
            f.write(f"  Max: {pareto_df['StdDev'].max():.4f}\n")


if __name__ == "__main__":
    """
    PyEGRO Robust Optimization Module - Full Documentation and Examples
    ================================================================
    
    This module provides three ways to perform robust optimization:
    1. Using InitialDesign class with direct function evaluation
    2. Using data_info.json for an existing setup
    3. Using trained surrogate models for efficient optimization
    
    The Borehole function is used as an example throughout this documentation
    as it's a well-known benchmark for robust optimization.
    """
    
    import numpy as np
    from PyEGRO.doe.initial_design import InitialDesign
    from PyEGRO.meta.gpr_utils import DeviceAgnosticGPR
    from PyEGRO.robustopt.mcs import (
        run_robust_optimization, 
        save_optimization_results
    )
    import json
    
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
    # Option 1: Direct Function Evaluation
    #==========================================================================
    print("\nOption 1: Direct Function Evaluation")
    print("=" * 50)
    
    # Step 1: Create InitialDesign instance
    design = InitialDesign(
        objective_function=borehole_function,
        output_dir='DATA_PREPARATION',
        show_progress=True
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
    
    # Step 4: Run optimization with direct function evaluation
    results1 = run_robust_optimization(
        true_func=borehole_function,
        data_info=design.data_info,
        mcs_samples=10000,
        pop_size=50,
        n_gen=100,
        save_dir='RESULT_DIRECT'
    )
    
    save_optimization_results(
        results=results1,
        data_info=design.data_info,
        save_dir='RESULT_DIRECT'
    )
    
    #==========================================================================
    # Option 2: Using data_info.json
    #==========================================================================
    print("\nOption 2: Using data_info.json")
    print("=" * 50)
    
    # Load existing problem definition
    with open('DATA_PREPARATION/data_info.json', 'r') as f:
        data_info = json.load(f)
    
    results2 = run_robust_optimization(
        true_func=borehole_function,
        data_info=data_info,
        mcs_samples=10000,
        pop_size=50,
        n_gen=100,
        save_dir='RESULT_FROM_JSON'
    )
    
    save_optimization_results(
        results=results2,
        data_info=data_info,
        save_dir='RESULT_FROM_JSON'
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
        mcs_samples=10000,
        pop_size=50,
        n_gen=100
    )
    
    save_optimization_results(
        results=results3,
        data_info=data_info
    )
    
