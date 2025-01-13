"""
Examples demonstrating different use cases of PyEGRO's EGO implementation.

This script provides multiple examples of using the EGO module for different
optimization scenarios and configurations.
"""

import numpy as np
import pandas as pd
import torch
from scipy.stats import qmc
from PyEGRO.ego import EfficientGlobalOptimization, TrainingConfig

# Example 1: Simple 1D Function Optimization
def example_1d():
    """Optimize a simple 1D function."""
    print("\nExample 1: Simple 1D Function Optimization")
    print("------------------------------------------")
    
    # Define objective function
    def simple_1d_func(x):
        """Simple 1D function with multiple local minima."""
        return (np.sin(3*x) + 0.3*x**2).reshape(-1, 1)
    
    # Set problem parameters
    bounds = np.array([[-3, 3]])
    variable_names = ['x']
    
    # Create initial data
    n_initial = 5
    X_initial = np.linspace(-3, 3, n_initial).reshape(-1, 1)
    y_initial = simple_1d_func(X_initial)
    initial_data = pd.DataFrame(X_initial, columns=variable_names)
    initial_data['y'] = y_initial
    
    # Configure and run optimization
    config = TrainingConfig(
        max_iterations=20,
        rmse_threshold=0.001,
        acquisition_name="ei",
        acquisition_params={"xi": 0.01}
    )
    
    ego = EfficientGlobalOptimization(
        objective_func=simple_1d_func,
        bounds=bounds,
        variable_names=variable_names,
        config=config,
        initial_data=initial_data
    )
    
    history = ego.run()
    return history

# Example 2: 2D Branin Function
def example_2d():
    """Optimize the 2D Branin function."""
    print("\nExample 2: 2D Branin Function Optimization")
    print("------------------------------------------")
    
    # Define Branin function
    def branin(x):
        """Branin function - classic 2D optimization test problem."""
        x1, x2 = x[:, 0], x[:, 1]
        term1 = x2 - 5.1/(4*np.pi**2)*x1**2 + 5/np.pi*x1 - 6
        term2 = 10*(1-1/(8*np.pi))*np.cos(x1)
        return (term1**2 + term2 + 10).reshape(-1, 1)
    
    # Set problem parameters
    bounds = np.array([[-5, 10], [0, 15]])
    variable_names = ['x1', 'x2']
    
    # Create initial data using Latin Hypercube Sampling
    n_initial = 10
    sampler = qmc.LatinHypercube(d=2)
    initial_points = sampler.random(n=n_initial)
    initial_points = qmc.scale(initial_points, bounds[:, 0], bounds[:, 1])
    
    initial_data = pd.DataFrame(initial_points, columns=variable_names)
    initial_data['y'] = branin(initial_points)
    
    # Configure and run optimization
    config = TrainingConfig(
        max_iterations=50,
        rmse_threshold=0.001,
        acquisition_name="eigf",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    
    ego = EfficientGlobalOptimization(
        objective_func=branin,
        bounds=bounds,
        variable_names=variable_names,
        config=config,
        initial_data=initial_data
    )
    
    history = ego.run()
    return history

# Example 3: Higher Dimensional Problem
def example_high_dim():
    """Optimize a higher dimensional problem."""
    print("\nExample 3: Higher Dimensional Optimization")
    print("------------------------------------------")
    
    # Define high-dimensional function
    def high_dim_func(x):
        """Simple high-dimensional quadratic function."""
        return np.sum(x**2, axis=1).reshape(-1, 1)
    
    # Set problem parameters
    dim = 5
    bounds = np.array([[-5, 5]]*dim)
    variable_names = [f'x{i+1}' for i in range(dim)]
    
    # Create initial data
    n_initial = 20
    sampler = qmc.LatinHypercube(d=dim)
    initial_points = sampler.random(n=n_initial)
    initial_points = qmc.scale(initial_points, bounds[:, 0], bounds[:, 1])
    
    initial_data = pd.DataFrame(initial_points, columns=variable_names)
    initial_data['y'] = high_dim_func(initial_points)
    
    # Configure and run optimization
    config = TrainingConfig(
        max_iterations=100,
        rmse_threshold=0.001,
        acquisition_name="eigf",
        training_iter=300,  # More training iterations for higher dimensions
        early_stopping_patience=30
    )
    
    ego = EfficientGlobalOptimization(
        objective_func=high_dim_func,
        bounds=bounds,
        variable_names=variable_names,
        config=config,
        initial_data=initial_data
    )
    
    history = ego.run()
    return history



if __name__ == "__main__":
    # Set random seeds for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    
    # Run examples
    history_1d = example_1d()
    history_2d = example_2d()
    history_high_dim = example_high_dim()

    print("\nAll examples completed successfully!")