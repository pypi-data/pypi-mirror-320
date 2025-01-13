"""
PyEGRO Sensitivity Analysis Module
--------------------------------
This module provides tools for performing sensitivity analysis on both analytical functions
and trained surrogate models using Sobol indices.
"""

from .sobol import SobolAnalyzer

__version__ = "1.0.0"
__author__ = "Thanasak Wanglomklang"
__email__ = "thanasak.wang@gmail.com"
__description__ = "Sensitivity analysis tools for PyEGRO"

def print_usage():
    """Print detailed usage instructions for the sensitivity analysis module."""
    usage = """
PyEGRO Sensitivity Analysis Module
=================================
Version: {version}

This module provides tools for performing Sobol sensitivity analysis using either
true functions or trained surrogate models. It supports three different approaches
to meet various use cases.

Installation
------------
The sensitivity module is part of the PyEGRO package:
    pip install pyegro

Available Classes
---------------
SobolAnalyzer : Main class for performing Sobol sensitivity analysis
    - Supports both true functions and surrogate models
    - Provides convergence analysis
    - Generates visualizations
    - Handles GPU acceleration when available

Usage Examples
-------------
Three ways to use the SobolAnalyzer:

1. With InitialDesign (Recommended):
    ```python
    from pyegro.initial_design import InitialDesign
    from pyegro.sensitivity import SobolAnalyzer
    
    # First create initial design
    design = InitialDesign(objective_function=your_function)
    
    # Add variables
    design.add_design_variable(
        name='x1',
        range_bounds=[-5, 5],
        cov=0.1
    )
    
    # Generate samples
    design.run(num_samples=50)
    
    # Create analyzer from design
    analyzer = SobolAnalyzer.from_initial_design(design)
    
    # Run analysis
    results = analyzer.run_analysis(
        true_func=your_function,
        n_samples=8192,
        calc_second_order=False  # Only first and total order indices
    )
    ```

2. Using data_info.json:
    ```python
    from pyegro.sensitivity import SobolAnalyzer
    
    # Initialize analyzer with data info
    analyzer = SobolAnalyzer(
        data_info_path="path/to/data_info.json",
        output_dir="sensitivity_results"
    )
    
    # Run analysis
    results = analyzer.run_analysis(
        true_func=your_function,
        n_samples=8192,
        sample_sizes=[256, 512, 1024, 2048, 4096, 8192]  # For convergence study
    )
    ```

3. Using Surrogate Model:
    ```python
    from pyegro.sensitivity import SobolAnalyzer
    
    # Initialize analyzer with both model and data info
    analyzer = SobolAnalyzer(
        model_path="path/to/model",
        data_info_path="path/to/data_info.json",
        output_dir="sensitivity_results"
    )
    
    # Run analysis
    results = analyzer.run_analysis(
        n_samples=8192,
        calc_second_order=False
    )
    ```

Key Features
-----------
1. Multiple Analysis Options:
   - True function evaluation
   - Surrogate model prediction
   - GPU acceleration for surrogate models
   
2. Comprehensive Results:
   - First-order indices (S1)
   - Total-order indices (ST)
   - Optional second-order indices (S2)
   - Confidence intervals
   
3. Convergence Analysis:
   - Multiple sample sizes
   - Convergence plots
   - Statistical validation

4. Progress Tracking:
   - Real-time progress bars
   - Time estimates
   - Status information

Required Files
-------------
1. For InitialDesign approach:
   - No additional files needed
   - Everything is handled automatically

2. When using data_info.json:
   Must contain:
   - variables: List of variable information
   - variable_names: List of variable names
   - input_bound: List of [min, max] bounds
   - total_variables: Total number of variables

3. For surrogate model analysis:
   Model directory should contain:
   - gpr_model.pth: Trained GPR model
   - scaler_X.pkl: Input scaler
   - scaler_y.pkl: Output scaler

Output Files
-----------
Each analysis generates:
1. sobol_results.json: Raw sensitivity indices
   - Contains results for all sample sizes
   - Includes confidence intervals
   - JSON format for easy processing

2. sensitivity_indices.csv: Final indices
   - Summary of final results
   - Easy to import into other tools
   - CSV format for spreadsheet compatibility

3. convergence_plot.png: Convergence visualization
   - Shows how indices converge
   - Separate plots for S1 and ST
   - Error bars included

4. sensitivity_indices.png: Bar plot
   - Visual comparison of indices
   - Error bars for uncertainty
   - Publication-ready quality

Sample Size Notes
---------------
Base sample size (N) will be multiplied based on:
- N*(2D+2) samples if calc_second_order=False
- N*(2D+2+((D-1)*D)/2) samples if calc_second_order=True
Where D is the number of variables

For optimal results:
- Use powers of 2 for sample sizes
- Start with small samples for quick tests
- Use larger samples for final analysis
- Monitor convergence behavior

For more information, visit:
https://github.com/twanglom/pyegro
""".format(version=__version__)
    
    print(usage)

def get_version():
    """Return the current version of the sensitivity module."""
    return __version__

def get_citation():
    """Return citation information for the sensitivity module."""
    citation = """
To cite this work, please use:

@software{pyegro_sensitivity,
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
    'SobolAnalyzer',
    'print_usage',
    'get_version',
    'get_citation'
]

# Optional: Print version on import
print(f"PyEGRO Sensitivity Analysis Module v{__version__}")