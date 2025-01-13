"""
PyEGRO Efficient Global Optimization (EGO) Module
-----------------------------------------------
This module implements Efficient Global Optimization (EGO) algorithms for robust 
optimization problems, featuring multiple acquisition functions and comprehensive 
configuration options.
"""

from .config import TrainingConfig
from .model import GPRegressionModel
from .training import EfficientGlobalOptimization

__version__ = "1.0.0"
__author__ = "Thanasak Wanglomklang"
__email__ = "thanasak.wang@gmail.com"
__description__ = "Efficient Global Optimization implementation for PyEGRO"

# Set random seeds for reproducibility
import numpy as np
import torch
np.random.seed(42)
torch.manual_seed(42)

def print_usage():
    """Print detailed usage instructions for the EGO module."""
    usage = """
PyEGRO Efficient Global Optimization Module
=========================================
Version: {version}

This module provides a comprehensive implementation of Efficient Global Optimization (EGO)
with support for multiple acquisition functions and robust optimization capabilities.

Installation
------------
The EGO module is part of the PyEGRO package:
    pip install pyegro

Available Classes
---------------
EfficientGlobalOptimization : Main optimization class
    - Multiple acquisition functions
    - Configurable training parameters
    - Built-in visualization tools
    
TrainingConfig : Configuration class
    - Customizable optimization parameters
    - Stopping criteria settings
    - Training control options

GPRegressionModel : Gaussian Process model
    - Surrogate modeling capabilities
    - Uncertainty quantification
    - GPU acceleration support

Key Features
-----------
1. Acquisition Functions:
   - Expected Improvement (EI) and Boosting the Exploration term (𝜁-EI)
   - Probability of Improvement (PI)
   - Lower Confidence Bound (LCB)
   - E3I (Exploration Enhanced Expected Improvement )
   - EIGF (Expected Improvement for Global Fit)
   - CRI3 (Distance-Enhanced Gradient )

2. Training Options and Stop criteria:
   - Maximum iterations 
   - RMSE thresholds
   - Patience settings
   - Relative improvement criteria
   - Device selection (CPU/GPU)

3. Visualization Tools:
   - 1D and 2D problem visualization
   - Convergence tracking
   - Uncertainty plots

4. Progress Monitoring:
   - Detailed console output
   - Rich progress tracking
   - Comprehensive metrics

Usage Examples
-------------
1. With Generated Initial Data:
```python
import numpy as np
import pandas as pd
from pyegro.ego import EfficientGlobalOptimization, TrainingConfig

# Define objective function
def objective_function(x):
    return np.sum(x**2, axis=1).reshape(-1, 1)

# Setup problem
bounds = np.array([[-5, 5], [-5, 5]])
variable_names = ['x1', 'x2']

# Generate initial data
n_initial = 5
initial_x = np.random.uniform(bounds[:, 0], bounds[:, 1], 
                           size=(n_initial, len(variable_names)))
initial_y = objective_function(initial_x)
initial_data = pd.DataFrame(initial_x, columns=variable_names)
initial_data['y'] = initial_y

# Configure and run
config = TrainingConfig(
    max_iterations=20,
    rmse_threshold=0.001,
    acquisition_name="eigf"
)
ego = EfficientGlobalOptimization(
    objective_func=objective_function,
    bounds=bounds,
    variable_names=variable_names,
    config=config,
    initial_data=initial_data
)
history = ego.run()
```

2. With Existing Data:
```python
import json
import pandas as pd
from pyegro.ego import EfficientGlobalOptimization, TrainingConfig

# Load existing data
with open('DATA_PREPARATION/data_info.json', 'r') as f:
    data_info = json.load(f)
initial_data = pd.read_csv('DATA_PREPARATION/training_data.csv')

# Setup from data
bounds = np.array(data_info['input_bound'])
variable_names = [var['name'] for var in data_info['variables']]

# Configure and run
config = TrainingConfig(
    max_iterations=100,
    rmse_threshold=0.001,
    acquisition_name="eigf"
)
ego = EfficientGlobalOptimization(
    objective_func=objective_function,
    bounds=bounds,
    variable_names=variable_names,
    config=config,
    initial_data=initial_data
)
history = ego.run()
```

Configuration Options
-------------------
TrainingConfig Parameters:
- max_iterations: Maximum optimization iterations
- rmse_threshold: Early stopping RMSE threshold
- rmse_patience: Iterations without improvement before stopping
- relative_improvement: Minimum required improvement
- acquisition_name: Acquisition function name
- acquisition_params: Acquisition function parameters
- training_iter: GP model training iterations
- verbose: Print detailed information
- show_summary: Show parameter summary
- device: Training device ('cpu' or 'cuda')
- save_dir: Results and model save directory

Acquisition Functions
-------------------
1. Expected Improvement (EI):
   - Name: "ei"
   - Parameters: xi (exploration weight)
   
2. Probability of Improvement (PI):
   - Name: "pi"
   - Parameters: xi (exploration weight)
   
3. Lower Confidence Bound (LCB):
   - Name: "lcb"
   - Parameters: beta (exploration-exploitation trade-off)
   
4. E3I:
   - Name: "e3i"
   - Parameters: n_weights, n_samples
   
5. EIGF:
   - Name: "eigf"
   - No additional parameters
   
6. CRI3:
   - Name: "cri3"
   - No additional parameters

Output Files
-----------
Each optimization run generates:
1. optimization_history.json:
   - Iteration details
   - Objective values
   - Model parameters
   
2. trained_model.pth:
   - Final GP model
   - Model hyperparameters
   - Training configuration

3. visualization.png:
   - Optimization progress
   - Uncertainty plots
   - For 1D/2D problems only

For more information, visit:
https://github.com/twanglom/pyegro
""".format(version=__version__)
    
    print(usage)

def get_version():
    """Return the current version of the EGO module."""
    return __version__

def get_citation():
    """Return citation information for the EGO module."""
    citation = """
To cite this work, please use:

@software{pyegro_ego,
    title={PyEGRO: Python Efficient Global Robust Optimization},
    author={Thanasak Wanglomklang},
    year={2024},
    version={""" + __version__ + """},
    url={https://github.com/twanglom/pyegro}
}
"""
    return citation

# Module level documentation
__all__ = [
    'EfficientGlobalOptimization',
    'TrainingConfig',
    'GPRegressionModel',
    'print_usage',
    'get_version',
    'get_citation'
]

# Optional: Print version on import
print(f"PyEGRO EGO Module v{__version__}")