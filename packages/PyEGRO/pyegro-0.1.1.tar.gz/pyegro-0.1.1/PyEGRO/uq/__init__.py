"""
PyEGRO Uncertainty Quantification Module
--------------------------------------
This module provides tools for uncertainty quantification and propagation using
Monte Carlo Simulation with support for both direct evaluation and surrogate models.
"""

from .mcs import UncertaintyPropagation, DeviceAgnosticGPR, GPRegressionModel

__version__ = "1.0.0"
__author__ = "Thanasak Wanglomklang"
__email__ = "thanasak.wang@gmail.com"
__description__ = "Uncertainty Quantification tools using Monte Carlo Simulation for PyEGRO"

def print_usage():
    """Print detailed usage instructions for the UQ module."""
    usage = """
PyEGRO Uncertainty Quantification Module
======================================
Version: {version}

This module provides comprehensive tools for uncertainty quantification and propagation 
using Monte Carlo Simulation, supporting both direct function evaluation and surrogate models.

Installation
------------
The UQ module is part of the PyEGRO package:
    pip install pyegro

Available Classes
---------------
UncertaintyPropagation : Main uncertainty analysis class
    - Monte Carlo Simulation
    - Variable information display
    - Progress tracking
    - Results visualization

DeviceAgnosticGPR : GPU-enabled surrogate model handler
    - Automatic device selection
    - Batch prediction support
    - Memory optimization

GPRegressionModel : Base GPR model
    - Matérn 2.5 kernel with ARD
    - Uncertainty estimation
    - Hardware acceleration

Key Features
-----------
1. Uncertainty Analysis:
   - Monte Carlo sampling
   - Both aleatory and epistemic uncertainty
   - Automatic variable detection
   - Progress tracking

2. Variable Types Support:
   - Design variables (deterministic/uncertain)
   - Environmental variables
   - Multiple distribution types
   - Automatic correlation handling

3. Hardware Support:
   - Automatic GPU detection
   - CPU fallback support
   - Batch processing
   - Memory optimization

4. Visualization:
   - Uncertainty bounds
   - Response surfaces
   - Correlation matrices
   - Statistical summaries

Usage Examples
-------------
1. Using InitialDesign (Recommended):
```python
from pyegro.doe.initial_design import InitialDesign
from pyegro.UQ.uqmcs import UncertaintyPropagation

# Create initial design
design = InitialDesign(
    objective_function=your_function,
    output_dir='DATA_PREPARATION'
)

# Add variables
design.add_design_variable(
    name='x1',
    range_bounds=[-5, 5],
    cov=0.1,
    description='first variable'
)

# Run uncertainty analysis
propagation = UncertaintyPropagation.from_initial_design(
    design,
    output_dir='UQ_RESULTS',
    show_variables_info=True
)

results = propagation.run_analysis(
    num_design_samples=1000,
    num_mcs_samples=100000
)
```

2. Using Existing Data:
```python
from pyegro.UQ.uqmcs import UncertaintyPropagation

# Initialize with data info
propagation = UncertaintyPropagation(
    data_info_path='data_info.json',
    true_func=your_function,
    output_dir='UQ_RESULTS',
    show_variables_info=True
)

results = propagation.run_analysis()
```

3. Using Surrogate Model:
```python
from pyegro.UQ.uqmcs import UncertaintyPropagation

# Initialize with surrogate
propagation = UncertaintyPropagation(
    data_info_path='data_info.json',
    model_path='MODEL_DIR',
    use_gpu=True,
    show_variables_info=True
)

results = propagation.run_analysis()
```

Configuration Options
-------------------
UncertaintyPropagation Parameters:
- data_info_path: Configuration file path
- true_func: Objective function (optional)
- model_path: Surrogate model path (optional)
- use_gpu: GPU acceleration flag
- output_dir: Results directory
- show_variables_info: Display variable details
- random_seed: Reproducibility control

Variable Information Display
--------------------------
For each variable shows:
1. Design Variables:
   - Name and description
   - Value range
   - Coefficient of variation
   - Variable type (deterministic/uncertain)
   - Distribution type

2. Environmental Variables:
   - Name and description
   - Distribution type
   - Distribution parameters
   - Range or moments

Output Files
-----------
Each analysis generates:
1. uncertainty_propagation_results.csv:
   - Design points
   - Mean responses
   - Standard deviations
   - Confidence intervals

2. uncertainty_analysis.png:
   - Response surface plots
   - Uncertainty bounds
   - Correlation matrices

3. analysis_summary.json:
   - Statistical summaries
   - Range information
   - Analysis parameters

Progress Tracking
---------------
During analysis, displays:
- Progress percentage
- Time elapsed/remaining
- Current iteration
- Hardware utilization

For more information, visit:
https://github.com/twanglom/pyegro
""".format(version=__version__)
    
    print(usage)

def get_version():
    """Return the current version of the UQ module."""
    return __version__

def get_citation():
    """Return citation information for the UQ module."""
    citation = """
To cite this work, please use:

@software{pyegro_uncertainty_quantification,
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
    'UncertaintyPropagation',
    'DeviceAgnosticGPR',
    'GPRegressionModel',
    'print_usage',
    'get_version',
    'get_citation'
]

# Optional: Print version on import
print(f"PyEGRO Uncertainty Quantification Module v{__version__}")