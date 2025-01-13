"""
PyEGRO Robust Optimization Module
--------------------------------
This module provides tools for robust optimization using various uncertainty 
quantification approaches including Monte Carlo Simulation (MCS) and 
Polynomial Chaos Expansion (PCE).

Available Methods:
----------------
1. Monte Carlo Simulation (MCS):
   - Direct sampling approach
   - Accurate but computationally intensive
   - Suitable for complex uncertainty distributions

2. Polynomial Chaos Expansion (PCE):
   - Efficient spectral method
   - Faster convergence for smooth responses
   - Better for higher-dimensional problems

Key Features:
-----------
- Multiple uncertainty quantification methods
- Support for both design and environmental variables
- Direct function and surrogate model evaluation
- Comprehensive visualization tools
- Progress tracking and performance metrics
- Hardware acceleration support (CPU/GPU)
"""

from .mcs import (
    RobustOptimizationProblemMCS,
    run_robust_optimization as run_mcs_optimization
)

from .pce import (
    RobustOptimizationProblemPCE,
    PCESampler,
    run_robust_optimization as run_pce_optimization
)

from .visualization import (
    ParameterInformationDisplay,
    OptimizationVisualizer
)

from meta.gpr_utils import (
    GPRegressionModel,
    DeviceAgnosticGPR
)

__version__ = "1.0.0"
__author__ = "Thanasak Wanglomklang"
__email__ = "thanasak.wang@gmail.com"
__description__ = "Robust Optimization tools using MCS and PCE for PyEGRO"

__all__ = [
    # MCS optimization
    'RobustOptimizationProblemMCS',
    'run_mcs_optimization',
    
    # PCE optimization
    'RobustOptimizationProblemPCE',
    'PCESampler',
    'run_pce_optimization',
    
    # Visualization utilities
    'ParameterInformationDisplay',
    'OptimizationVisualizer',
    
    # GPR utilities
    'GPRegressionModel',
    'DeviceAgnosticGPR'
]

def print_usage():
    """Print detailed usage instructions."""
    usage = """
PyEGRO Robust Optimization Module
================================

This module provides comprehensive tools for robust optimization using multiple
uncertainty quantification approaches.

Installation
------------
The robust optimization module is part of the PyEGRO package:
    pip install pyegro

Available Methods
---------------
1. Monte Carlo Simulation (MCS):
   - Traditional sampling-based approach
   - High accuracy with sufficient samples
   - Flexible distribution support
   - Example usage:
     ```python
     from pyegro.robustopt import run_mcs_optimization
     results = run_mcs_optimization(
         data_info=data_info,
         true_func=objective_function,  # or gpr_handler for surrogate
         pop_size=50,
         n_gen=100
     )
     ```

2. Polynomial Chaos Expansion (PCE):
   - Spectral uncertainty quantification
   - Efficient for smooth responses
   - Better convergence properties
   - Example usage:
     ```python
     from pyegro.robustopt import run_pce_optimization
     results = run_pce_optimization(
         data_info=data_info,
         true_func=objective_function,  # or gpr_handler for surrogate
         pop_size=50,
         n_gen=100
     )
     ```

Key Features
-----------
1. Multiple Evaluation Options:
   - Direct function evaluation
   - Surrogate model evaluation
   - GPU acceleration support

2. Variable Types Support:
   - Design variables (deterministic/uncertain)
   - Environmental variables
   - Multiple distribution types

3. Optimization Features:
   - Multi-objective optimization
   - Progress tracking
   - Performance metrics
   - Result visualization

4. Visualization Capabilities:
   - Pareto front plots
   - Decision variable distributions
   - Convergence history
   - Summary statistics

Example Usage
------------
1. Using Initial Design:
```python
from pyegro.doe import InitialDesign
from pyegro.robustopt import run_mcs_optimization

# Create design
design = InitialDesign(objective_function=your_function)
design.add_design_variable(name='x1', range_bounds=[-5, 5], cov=0.1)
design.add_env_variable(name='e1', distribution='uniform', low=-1, high=1)

# Run optimization
results = run_mcs_optimization(
    data_info=design.data_info,
    true_func=your_function
)
```

2. Using Surrogate Model:
```python
from pyegro.meta_trainer import DeviceAgnosticGPR
from pyegro.robustopt import run_pce_optimization

# Load surrogate
gpr = DeviceAgnosticGPR(prefer_gpu=True)
gpr.load_model('your_model_dir')

# Run optimization
results = run_pce_optimization(
    data_info=data_info,
    gpr_handler=gpr
)
```

For more information, visit:
https://github.com/twanglom/pyegro
"""
    print(usage)

def get_version():
    """Return the current version of the module."""
    return __version__

def get_citation():
    """Return citation information."""
    citation = """
To cite this work, please use:

@software{pyegro_robust_optimization,
    title={PyEGRO: Python Efficient Global Robust Optimization},
    author={Thanasak Wanglomklang},
    year={2024},
    version={""" + __version__ + """},
    url={https://github.com/twanglom/pyegro}
}
"""
    return citation