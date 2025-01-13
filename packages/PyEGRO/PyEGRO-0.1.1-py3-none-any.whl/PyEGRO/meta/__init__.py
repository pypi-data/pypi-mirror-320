"""
PyEGRO MetaTrainer Module
------------------------
This module provides tools for training and managing Gaussian Process Regression (GPR)
models with comprehensive visualization and progress tracking capabilities.
"""

from .meta_trainer import MetaTraining, GPRegressionModel

__version__ = "1.0.0"
__author__ = "Thanasak Wanglomklang"
__email__ = "thanasak.wang@gmail.com"
__description__ = "Gaussian Process Regression training tools for PyEGRO"

def print_usage():
    """Print detailed usage instructions for the MetaTrainer module."""
    usage = """
PyEGRO MetaTrainer Module
========================
Version: {version}

This module provides comprehensive tools for training and managing Gaussian Process 
Regression (GPR) models with built-in visualization and progress tracking.

Installation
------------
The MetaTrainer module is part of the PyEGRO package:
    pip install pyegro

Available Classes
---------------
MetaTraining : Main training manager class
    - Comprehensive GPR model training
    - Progress tracking and visualization
    - Hardware optimization
    - Model evaluation and saving

GPRegressionModel : GPR model implementation
    - Matérn 2.5 kernel with ARD
    - Configurable hyperparameters
    - GPU acceleration support

Key Features
-----------
1. Training Management:
   - Automatic train/test splitting
   - Early stopping with patience
   - Progress tracking
   - Hardware optimization

2. Model Features:
   - Gaussian Process Regression
   - Matérn 2.5 kernel with ARD
   - Automatic hyperparameter optimization
   - Uncertainty quantification

3. Hardware Support:
   - Automatic GPU detection
   - CPU fallback support
   - Memory optimization
   - Device information display

4. Visualization:
   - Performance plots
   - Training progress
   - Model evaluation metrics
   - Hardware utilization

Usage Examples
-------------
1. Basic Usage:
```python
from pyegro.meta_trainer import MetaTraining

# Initialize trainer
meta = MetaTraining(
    test_size=0.3,           # 30% test data
    num_iterations=100,      # Max training iterations
    prefer_gpu=True,         # Use GPU if available
    show_progress=True       # Show progress bar
)

# Train model with default data
model, scaler_X, scaler_y = meta.train('training_data.csv')
```

2. Custom Data Usage:
```python
import pandas as pd
from pyegro.meta_trainer import MetaTraining

# Prepare your data
X = pd.DataFrame(...)  # Your features
y = ...                # Your targets

# Initialize trainer
meta = MetaTraining(
    test_size=0.2,             
    num_iterations=200,
    prefer_gpu=False,          
    show_progress=True,
    show_hardware_info=True,
    show_model_info=True,
    output_dir='my_results'
)

# Train with custom data
model = meta.train(X, y, custom_data=True)

# Make predictions
predictions, uncertainties = meta.predict(X_new)
```

Configuration Options
-------------------
MetaTraining Parameters:
- test_size: Train/test split ratio (default: 0.3)
- num_iterations: Maximum training iterations (default: 100)
- prefer_gpu: Use GPU when available (default: True)
- show_progress: Display progress bar (default: True)
- show_hardware_info: Show system details (default: True)
- show_model_info: Display model architecture (default: True)
- output_dir: Results directory (default: 'RESULT_MODEL_GPR')
- data_dir: Input data directory (default: 'DATA_PREPARATION')

Model Architecture
----------------
1. Kernel:
   - Matérn 2.5 with ARD
   - Automatic lengthscale optimization
   - Noise parameter optimization

2. Mean Function:
   - Constant mean
   - Optimized during training

3. Optimizer:
   - Adam optimizer
   - Learning rate: 0.1
   - Early stopping patience: 20

Output Files
-----------
Each training run generates:
1. gpr_model.pth:
   - Trained model state
   - Model hyperparameters
   - Training configuration

2. scaler_X.pkl and scaler_y.pkl:
   - Feature scalers
   - Target scalers
   - Normalization parameters

3. performance/model_performance.png:
   - Training performance plot
   - Testing performance plot
   - R² and RMSE metrics

Progress Tracking
---------------
During training, displays:
- Progress percentage
- Current loss
- Best loss achieved
- Time elapsed/remaining
- Hardware utilization

Display Options
-------------
1. Hardware Information:
   - CPU/GPU specifications
   - Memory availability
   - CUDA version (if GPU)
   - PyTorch/GPyTorch versions

2. Model Information:
   - Architecture details
   - Training parameters
   - Dataset statistics
   - Variable names

3. Results Display:
   - Training/Testing RMSE
   - R² scores
   - Performance plots
   - Save locations

For more information, visit:
https://github.com/twanglom/pyegro
""".format(version=__version__)
    
    print(usage)

def get_version():
    """Return the current version of the MetaTrainer module."""
    return __version__

def get_citation():
    """Return citation information for the MetaTrainer module."""
    citation = """
To cite this work, please use:

@software{pyegro_meta_trainer,
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
    'MetaTraining',
    'GPRegressionModel',
    'print_usage',
    'get_version',
    'get_citation'
]

# Optional: Print version on import
print(f"PyEGRO MetaTrainer Module v{__version__}")