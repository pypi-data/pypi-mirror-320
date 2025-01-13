"""
Gaussian Process model implementations for EGO.

This module provides the GP model implementation used in the EGO process.
"""

import torch
import gpytorch
from typing import Dict, Union, List, Tuple
import warnings
from gpytorch.utils.warnings import GPInputWarning, NumericalWarning
warnings.filterwarnings("ignore", category=GPInputWarning)
warnings.filterwarnings("ignore", category=NumericalWarning)


class GPRegressionModel(gpytorch.models.ExactGP):
    """Gaussian Process Regression Model with Matérn kernel.
    
    This model uses a Matérn kernel with automatic relevance determination (ARD)
    and a constant mean function.
    
    Attributes:
        mean_module: Mean function for GP
        covar_module: Covariance function for GP (Matérn kernel with ARD)
    """
    
    def __init__(self, train_x: torch.Tensor, train_y: torch.Tensor, 
                 likelihood: gpytorch.likelihoods.Likelihood):
        """Initialize GP model.
        
        Args:
            train_x: Training input data
            train_y: Training target data
            likelihood: GPyTorch likelihood
        """
        super().__init__(train_x, train_y, likelihood)
        
        # Define mean and covariance functions
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(
            gpytorch.kernels.MaternKernel(
                nu=2.5,
                ard_num_dims=train_x.size(-1)
            )
        )
        
        # Set initial hyperparameters
        self.initialize_hyperparameters()
        
    def initialize_hyperparameters(self):
        """Set initial values for model hyperparameters."""
        self.covar_module.base_kernel.lengthscale = 1.0
        self.covar_module.outputscale = 1.0
        self.likelihood.noise_covar.noise = 1e-3

    def forward(self, x: torch.Tensor) -> gpytorch.distributions.MultivariateNormal:
        """Forward pass of GP model.
        
        Args:
            x: Input data
            
        Returns:
            MultivariateNormal distribution representing GP predictions
        """
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)
        
    def get_hyperparameters(self) -> Dict[str, Union[float, List[float]]]:
        """Get current hyperparameter values.
        
        Returns:
            Dictionary containing the current values of all hyperparameters
        """
        return {
            'lengthscales': self.covar_module.base_kernel.lengthscale.detach().cpu().numpy().tolist(),
            'outputscale': float(self.covar_module.outputscale.detach().cpu().numpy()),
            'noise': float(self.likelihood.noise_covar.noise.detach().cpu().numpy())
        }
        
    def predict(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Make predictions with the GP model.
        
        Args:
            x: Input points to make predictions at
            
        Returns:
            Tuple of (mean predictions, standard deviations)
        """
        self.eval()
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            observed_pred = self.likelihood(self(x))
            return observed_pred.mean, observed_pred.stddev