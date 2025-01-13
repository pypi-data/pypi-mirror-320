

"""
Utility functions for EGO.

This module provides helper functions and utilities for the EGO process.
"""

import os
import torch
import gpytorch
import numpy as np
import pandas as pd
import json
import joblib
from typing import Dict, List, Tuple, Optional
from scipy.stats import skew, kurtosis
from sklearn.metrics import r2_score
# Local imports
from .config import TrainingConfig

def setup_directories(save_dir: str, create_plots: bool = True):
    """Create necessary directories for saving results.
    
    Args:
        save_dir: Base directory for saving results
        create_plots: Whether to create plots directory
    """
    os.makedirs(save_dir, exist_ok=True)
    if create_plots:
        os.makedirs(os.path.join(save_dir, 'plots'), exist_ok=True)
        os.makedirs(os.path.join(save_dir, 'animation'), exist_ok=True)

def evaluate_model_performance(model, likelihood, X_train: torch.Tensor, 
                           y_train: torch.Tensor) -> Dict[str, float]:
    """Calculate model performance metrics using LOOCV.
    
    Args:
        model: GP model
        likelihood: Model likelihood
        X_train: Training input data
        y_train: Training target data
        
    Returns:
        Dictionary of performance metrics including LOOCV-RMSE
    """
    # Calculate LOOCV-RMSE
    loocv_errors = []
    for i in range(len(X_train)):
        X_train_loocv = torch.cat((X_train[:i], X_train[i+1:]), dim=0)
        y_train_loocv = torch.cat((y_train[:i], y_train[i+1:]), dim=0)
        
        model.set_train_data(X_train_loocv, y_train_loocv, strict=False)
        model.eval()
        likelihood.eval()
        
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            pred = likelihood(model(X_train[i:i+1]))
            loocv_error = (y_train[i].item() - pred.mean.item()) ** 2
            loocv_errors.append(loocv_error)
    
    # Reset model data
    model.set_train_data(X_train, y_train, strict=False)
    
    # Calculate LOOCV-RMSE
    loocv_rmse = float(np.sqrt(np.mean(loocv_errors)))
    
    # Get predictions for all points
    model.eval()
    likelihood.eval()
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        predictions = likelihood(model(X_train))
        y_pred = predictions.mean.cpu().numpy()
        y_true = y_train.cpu().numpy()
    
    # Calculate metrics
    return {
        'rmse': loocv_rmse,  # Using LOOCV-RMSE
        'r2': float(r2_score(y_true, y_pred)),
        **calculate_regression_diagnostics(y_true, y_pred)
    }

def calculate_regression_diagnostics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """Calculate comprehensive regression diagnostic metrics.
    
    Args:
        y_true: True target values
        y_pred: Predicted target values
        
    Returns:
        Dictionary containing various regression metrics
    """
    residuals = y_true.flatten() - y_pred.flatten()
    
    return {
        'mean_residual': float(np.mean(residuals)),
        'residual_std': float(np.std(residuals)),
        'max_residual': float(np.max(residuals)),
        'min_residual': float(np.min(residuals)),
        'residual_skewness': float(skew(residuals)),
        'residual_kurtosis': float(kurtosis(residuals))
    }

def train_gp_model(model, likelihood, X_train: torch.Tensor, 
                 y_train: torch.Tensor, config: TrainingConfig):
    """Train GP model with optimization settings.
    
    Args:
        model: GP model to train
        likelihood: Model likelihood
        X_train: Training input data
        y_train: Training target data
        config: Training configuration
    """
    model.train()
    likelihood.train()
    
    optimizer = torch.optim.Adam([
        {'params': model.parameters(), 'lr': config.learning_rate}
    ])
    
    mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)
    
    best_loss = float('inf')
    patience_counter = 0

    with gpytorch.settings.cholesky_jitter(config.jitter):
        for i in range(config.training_iter):
            try:
                optimizer.zero_grad()
                output = model(X_train)
                loss = -mll(output, y_train)
                loss.backward()
                optimizer.step()
                
                current_loss = loss.item()
                
                if current_loss < best_loss:
                    best_loss = current_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    
                if patience_counter >= config.early_stopping_patience:
                    if config.verbose:
                        print(f"Early stopping at iteration {i}")
                    break
                    
            except RuntimeError as e:
                if "cholesky" in str(e) and config.verbose:
                    print(f"Cholesky error at iteration {i}, continuing...")
                    continue
                raise e

def save_metrics(metrics_df: pd.DataFrame, iteration: int, acquisition_type: str,
                rmse: float, r2: float, best_value: float, mean_uncertainty: float,
                y_true: np.ndarray, y_pred: np.ndarray, save_dir: str):
    """Save optimization metrics to CSV file.
    
    Args:
        metrics_df: DataFrame to store metrics
        iteration: Current iteration number
        acquisition_type: Name of acquisition function
        rmse: Current RMSE value
        r2: Current R² score
        best_value: Best objective value found
        mean_uncertainty: Mean prediction uncertainty
        y_true: True objective values
        y_pred: Predicted values
        save_dir: Directory to save metrics
    """
    # Get current timestamp
    timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate regression diagnostics
    regression_metrics = calculate_regression_diagnostics(y_true, y_pred)
    
    # Create metrics dictionary
    metrics_dict = {
        'timestamp': timestamp,
        'iteration': iteration,
        'acquisition_type': acquisition_type,
        'rmse': rmse,
        'r2_score': r2,
        'best_value': best_value,
        'mean_uncertainty': mean_uncertainty,
        **regression_metrics
    }
    
    # Check for existing iteration
    if not metrics_df.empty:
        existing_iteration = metrics_df[metrics_df['iteration'] == iteration]
        if not existing_iteration.empty:
            # Update existing row
            metrics_df.loc[metrics_df['iteration'] == iteration] = metrics_dict
            return metrics_df
    
    # Add new row
    new_metrics = pd.DataFrame([metrics_dict])
    updated_metrics = pd.concat([metrics_df, new_metrics], ignore_index=True)
    
    # Save to file
    metrics_file = os.path.join(save_dir, 'optimization_metrics.csv')
    if not os.path.exists(metrics_file):
        updated_metrics.to_csv(metrics_file, index=False)
    else:
        # Append without header if file exists
        updated_metrics.tail(1).to_csv(metrics_file, mode='a', header=False, index=False)
    
    return updated_metrics

def save_infill_sample(X_next: np.ndarray, y_next: np.ndarray, 
                      variable_names: list, save_dir: str):
    """Save infill sample to CSV file.
    
    Args:
        X_next: New input point
        y_next: Evaluated objective value
        variable_names: Names of input variables
        save_dir: Directory to save data
    """
    # Get current timestamp
    timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create data dictionary
    data_dict = {
        'timestamp': timestamp,
        **{name: val for name, val in zip(variable_names, X_next.flatten())},
        'y': y_next.flatten()[0]
    }
    
    # Create DataFrame for the new point
    point_data = pd.DataFrame([data_dict])
    
    # Save to infill_samples.csv
    infill_file = os.path.join(save_dir, 'infill_samples.csv')
    if not os.path.exists(infill_file):
        point_data.to_csv(infill_file, index=False)
    else:
        point_data.to_csv(infill_file, mode='a', header=False, index=False)

def save_model_data(model, likelihood, scalers: Dict, metadata: Dict, save_dir: str):
    """Save model, scalers, and metadata.
    
    Args:
        model: Trained GP model
        likelihood: Model likelihood
        scalers: Dictionary of data scalers
        metadata: Model metadata
        save_dir: Directory to save data
    """
    # Save model state
    state_dict = {
        'model': model.cpu().state_dict(),
        'likelihood': likelihood.cpu().state_dict(),
        'train_inputs': [x.cpu() for x in model.train_inputs],
        'train_targets': model.train_targets.cpu(),
        'input_size': model.train_inputs[0].shape[1]
    }
    
    torch.save(state_dict, os.path.join(save_dir, 'gpr_model.pth'))
    
    # Save scalers
    for name, scaler in scalers.items():
        joblib.dump(scaler, os.path.join(save_dir, f'scaler_{name}.pkl'))
    
    # Save metadata
    with open(os.path.join(save_dir, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4)

def load_model_data(save_dir: str) -> Dict:
    """Load saved model data.
    
    Args:
        save_dir: Directory containing saved model data
        
    Returns:
        Dictionary containing loaded model data
    """
    # Load model state
    state_dict = torch.load(os.path.join(save_dir, 'gpr_model.pth'))
    
    # Load scalers
    scalers = {
        'X': joblib.load(os.path.join(save_dir, 'scaler_X.pkl')),
        'y': joblib.load(os.path.join(save_dir, 'scaler_y.pkl'))
    }
    
    # Load metadata
    with open(os.path.join(save_dir, 'model_metadata.json'), 'r') as f:
        metadata = json.load(f)
        
    return {
        'state_dict': state_dict,
        'scalers': scalers,
        'metadata': metadata
    }

def get_device_info() -> Dict[str, str]:
    """Get information about the computing device.
    
    Returns:
        Dictionary containing device information
    """
    if torch.cuda.is_available():
        return {
            'device_type': 'GPU',
            'device_name': torch.cuda.get_device_name(0),
            'cuda_version': torch.version.cuda,
            'memory': f"{torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB"
        }
    else:
        import platform
        return {
            'device_type': 'CPU',
            'device_name': platform.processor(),
            'cuda_version': 'N/A',
            'memory': 'N/A'
        }

