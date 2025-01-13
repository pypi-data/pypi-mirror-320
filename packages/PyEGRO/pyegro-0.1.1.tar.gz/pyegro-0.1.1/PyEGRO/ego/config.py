"""
Configuration management for EGO training.

This module provides configuration classes and settings for the EGO training process.
"""

import torch
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class TrainingConfig:
    """Configuration class for EGO training parameters.
    
    Attributes:
        max_iterations: Maximum number of optimization iterations
        rmse_threshold: RMSE threshold for early stopping
        rmse_patience: Number of iterations without improvement before stopping
        relative_improvement: Minimum relative improvement required
        acquisition_name: Name of acquisition function
        acquisition_params: Parameters for the acquisition function
        training_iter: Number of training iterations for GP model
        verbose: Whether to print detailed training information
        show_summary: Whether to show parameter summary before training
        device: Device to use for training ('cpu' or 'cuda')
        save_dir: Directory to save results and models
        learning_rate: Learning rate for model optimization
        early_stopping_patience: Patience for early stopping during model training
        jitter: Jitter value for numerical stability
    """
    max_iterations: int = 100
    rmse_threshold: float = 0.001
    rmse_patience: int = 10
    relative_improvement: float = 0.01   # 10%
    acquisition_name: str = "ei"
    acquisition_params: Dict[str, Any] = field(default_factory=dict)
    training_iter: int = 100
    verbose: bool = False
    show_summary: bool = True
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    save_dir: str = "RESULT_MODEL_GPR"
    learning_rate: float = 0.01
    early_stopping_patience: int = 20
    jitter: float = 1e-3
    
    def __post_init__(self):
        """Initialize default acquisition parameters if not provided."""
        # Default parameters for different acquisition functions
        default_params = {
            "ei": {"xi": 0.01},
            "pi": {"xi": 0.01},
            "lcb": {"beta": 2.0},
            "e3i": {"n_weights": 50, "n_samples": 10},
            "eigf": {},
            "cri3": {}
        }
        
        if self.acquisition_name not in default_params:
            raise ValueError(f"Unsupported acquisition function: {self.acquisition_name}")
            
        # Update acquisition parameters with defaults if not provided
        if not self.acquisition_params:
            self.acquisition_params = default_params[self.acquisition_name]
        else:
            self.acquisition_params = {
                **default_params[self.acquisition_name],
                **self.acquisition_params
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "max_iterations": self.max_iterations,
            "rmse_threshold": self.rmse_threshold,
            "rmse_patience": self.rmse_patience,
            "relative_improvement": self.relative_improvement,
            "acquisition_name": self.acquisition_name,
            "acquisition_params": self.acquisition_params,
            "training_iter": self.training_iter,
            "learning_rate": self.learning_rate,
            "early_stopping_patience": self.early_stopping_patience,
            "jitter": self.jitter,
            "device": self.device,
            "save_dir": self.save_dir,
            "verbose": self.verbose,
            "show_summary": self.show_summary
        }