"""
PyEGRO Initial Design Module
---------------------------
This module provides tools for generating initial design samples with support for both
design and environmental variables, using adaptive distribution sampling methods.
"""

from .initial_design import InitialDesign, Variable

__version__ = "1.0.0"
__author__ = "Thanasak Wanglomklang"
__email__ = "thanasak.wang@gmail.com"
__description__ = "Initial design and sampling tools for PyEGRO"

def print_usage():
    """Print detailed usage instructions for the initial design module."""
    usage = """
PyEGRO Initial Design Module
===========================
Version: {version}

This module provides tools for generating initial design samples with support for both
design and environmental variables. It features adaptive distribution sampling and
real-time progress tracking.

Installation
------------
The initial design module is part of the PyEGRO package:
    pip install pyegro

Available Classes
---------------
InitialDesign : Main class for generating initial design samples
    - Supports both design and environmental variables
    - Provides progress tracking
    - Generates visualization
    - Saves comprehensive metadata

Variable : Dataclass for representing variables
    - Supports multiple variable types
    - Handles different distributions
    - Stores variable metadata

Usage Example
------------
Basic usage with design and environmental variables:

```python
from pyegro.initial_design import InitialDesign

# Define your objective function
def objective(x):
    return np.sum(x**2, axis=1)

# Create initial design instance
design = InitialDesign(
    objective_function=objective,
    show_progress=True,    # Show progress bar
    show_result=True       # Show final statistics
)

# Add design variable
design.add_design_variable(
    name='x1',
    range_bounds=[-5, 5],
    cov=0.1,
    distribution='normal'
)

# Add environmental variable
design.add_env_variable(
    name='env1',
    distribution='normal',
    mean=0.5,
    cov=0.1
)

# Generate samples
design.run(num_samples=50)
```

Key Features
-----------
1. Variable Types:
   - Design variables with range bounds
   - Environmental variables with distributions
   
2. Supported Distributions:
   - Normal distribution
   - Lognormal distribution
   - Uniform distribution 
   
3. Progress Tracking:
   - Real-time progress bars
   - Time estimates
   - Sample generation status
   
4. Results Display:
   - Summary statistics
   - File save locations
   - Completion status

Output Files
-----------
Each run generates:
1. training_data.csv:
   - Contains all generated samples
   - Includes objective function values
   - CSV format for easy processing

2. data_info.json:
   - Variable definitions and metadata
   - Input bounds
   - Total number of samples
   - Distribution parameters

Display Options
-------------
show_progress : bool = True
    - Shows progress during sample generation
    - Displays current sample number
    - Shows time remaining

show_result : bool = False
    - Shows summary statistics table
    - Displays file save locations
    - Shows completion message

Variable Configuration
--------------------
1. Design Variables:
   Required parameters:
   - name: Variable name
   - range_bounds: [min, max]
   - cov: Coefficient of variation
   - distribution: 'uniform', 'normal' or 'lognormal'
   - description: Optional description

2. Environmental Variables:
   For normal/lognormal:
   - name: Variable name
   - distribution: 'normal' or 'lognormal'
   - mean: Mean value
   - cov: Coefficient of variation
   - description: Optional description

   For uniform:
   - name: Variable name
   - distribution: 'uniform'
   - low: Lower bound
   - high: Upper bound
   - description: Optional description

For more information, visit:
https://github.com/twanglom/pyegro
""".format(version=__version__)
    
    print(usage)

def get_version():
    """Return the current version of the initial design module."""
    return __version__

def get_citation():
    """Return citation information for the initial design module."""
    citation = """
To cite this work, please use:

@software{pyegro_initial_design,
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
    'InitialDesign',
    'Variable',
    'print_usage',
    'get_version',
    'get_citation'
]

# Optional: Print version on import
# print(f"PyEGRO Initial Design Module v{__version__}")