

import torch
import gpytorch
import numpy as np
from typing import List, Tuple
from scipy.stats import norm
from abc import ABC, abstractmethod
from pymoo.core.problem import Problem
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.optimize import minimize
import pandas as pd
import os

class AcquisitionFunction(ABC):
    def __init__(self, model, likelihood, bounds, scaler_x, scaler_y):
        self.model = model
        self.likelihood = likelihood
        self.bounds = bounds
        self.scaler_x = scaler_x
        self.scaler_y = scaler_y
        
    @abstractmethod
    def evaluate(self, X):
        pass
        
    def optimize(self):
        problem = self._create_optimization_problem()
        algorithm = GA(pop_size=500, eliminate_duplicates=True)
        
        try:
            res = minimize(problem, algorithm, seed=1, verbose=False)
            X_next_scaled = np.array(res.X).reshape(-1, self.bounds.shape[0])
            X_next = self.scaler_x.inverse_transform(X_next_scaled)
        except Exception as e:
            print(f"Optimization failed: {str(e)}")
            X_next = np.random.uniform(
                low=[b[0] for b in self.bounds],
                high=[b[1] for b in self.bounds],
                size=(1, self.bounds.shape[0])
            )
        return X_next

    def _create_optimization_problem(self):
        return AcquisitionOptimizationProblem(
            acquisition_function=self,
            n_vars=self.bounds.shape[0],
            bounds=self.bounds,
            scaler_x=self.scaler_x
        )


class ExpectedImprovement(AcquisitionFunction):
    def __init__(self, model, likelihood, bounds, scaler_x, scaler_y, y_train, xi=0.2):
        super().__init__(model, likelihood, bounds, scaler_x, scaler_y)
        self.y_min = np.min(scaler_y.transform(y_train)) 
        self.xi = xi
        
    def evaluate(self, X):
        self.model.eval()
        self.likelihood.eval()
        
        device = next(self.model.parameters()).device
        X = torch.tensor(X, dtype=torch.float32).to(device)
        
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            pred = self.likelihood(self.model(X))
            mu = pred.mean
            sigma = pred.variance.sqrt()
            
        mu = mu.cpu().numpy()
        sigma = sigma.cpu().numpy()
        
        with np.errstate(divide='warn'):
            imp = self.y_min - mu - self.xi 
            Z = imp / (sigma + 1e-9)
            ei = imp * norm.cdf(Z) + sigma * norm.pdf(Z)
            ei[sigma == 0.0] = 0.0  
            
        return -ei  



class ExpectedImprovementGlobalFit(AcquisitionFunction):
    """
    Implementation of Expected Improvement for Global Fit (EIGF) criterion.
    Combines local improvement with global uncertainty for better model fit.
    """
    def init(self, model, likelihood, bounds, scaler_x, scaler_y):
        super().init(model, likelihood, bounds, scaler_x, scaler_y)

    def _find_nearest_point(self, X, X_train):
        """Find the nearest training point for each candidate point."""
        device = next(self.model.parameters()).device

        # Compute pairwise distances
        distances = torch.cdist(X, X_train)

        # Get indices of nearest points
        nearest_indices = torch.argmin(distances, dim=1)

        return nearest_indices

    def evaluate(self, X):
        self.model.eval()
        self.likelihood.eval()

        device = next(self.model.parameters()).device
        X = torch.tensor(X, dtype=torch.float32).to(device)
        X_train = self.model.train_inputs[0]
        y_train = self.model.train_targets

        # Find nearest training points
        nearest_indices = self._find_nearest_point(X, X_train)
        y_nearest = y_train[nearest_indices]

        # Get GP predictions
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            pred = self.likelihood(self.model(X))
            mean = pred.mean
            variance = pred.variance

        # Calculate local improvement component: (Ŷ(x) - y(x_j*))²
        local_improvement = (mean - y_nearest) ** 2

        # Global component is the prediction variance
        global_component = variance

        # Combined EIGF criterion from equation (19)
        eigf = local_improvement + global_component

        return -eigf.cpu().numpy()  # Negative for minimization
    


class PredictiveVariance(AcquisitionFunction):
    def evaluate(self, X):
        self.model.eval()
        self.likelihood.eval()
        
        device = next(self.model.parameters()).device
        X = torch.tensor(X, dtype=torch.float32).to(device)
        
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            pred = self.likelihood(self.model(X))
            variance = pred.variance
            
        return -variance.cpu().numpy()


class LowerConfidenceBound(AcquisitionFunction):
    def __init__(self, model, likelihood, bounds, scaler_x, scaler_y, beta=2.0):
        super().__init__(model, likelihood, bounds, scaler_x, scaler_y)
        self.beta = beta
        
    def evaluate(self, X):
        self.model.eval()
        self.likelihood.eval()
        
        device = next(self.model.parameters()).device
        X = torch.tensor(X, dtype=torch.float32).to(device)
        
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            pred = self.likelihood(self.model(X))
            mean = pred.mean
            std = pred.variance.sqrt()
            
        # For minimization, we want mean - beta * std
        lcb = (mean - self.beta * std).cpu().numpy()
        return lcb  # No need for negative since we want to minimize


class ProbabilityImprovement(AcquisitionFunction):
    def __init__(self, model, likelihood, bounds, scaler_x, scaler_y, y_train, xi=0.01):
        """
        Probability of Improvement acquisition function.
        
        Args:
            model: GP model
            likelihood: GP likelihood
            bounds: Input bounds
            scaler_x: Input scaler
            scaler_y: Output scaler
            y_train: Training targets
            xi: Exploration-exploitation trade-off parameter
        """
        super().__init__(model, likelihood, bounds, scaler_x, scaler_y)
        self.y_min = np.min(scaler_y.transform(y_train))  # Best observed value
        self.xi = xi  # Trade-off parameter
        
    def evaluate(self, X):
        self.model.eval()
        self.likelihood.eval()
        
        device = next(self.model.parameters()).device
        X = torch.tensor(X, dtype=torch.float32).to(device)
        
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            pred = self.likelihood(self.model(X))
            mean = pred.mean
            std = pred.variance.sqrt()
            
        # Move to numpy for probability calculations
        mean = mean.cpu().numpy()
        std = std.cpu().numpy()
        
        # Calculate improvement relative to best observed value
        # Add small epsilon to std to avoid division by zero
        epsilon = 1e-9
        z = (self.y_min - mean - self.xi) / (std + epsilon)
        
        # Calculate probability using Gaussian CDF
        pi = norm.cdf(z)
        
        return -pi  # Return negative since we're minimizing
    

class Criterion3(AcquisitionFunction):
    """
    Implementation of Criterion 3 from the paper:
    Crit(ξ) = (|∂f̂(ξ)/∂ξ|Δ(ξ) + Dj(ξ))ŝ(ξ)PDF(ξ)
    where:
    - |∂f̂(ξ)/∂ξ| is the gradient magnitude
    - Δ(ξ) is the distance to nearest sample
    - Dj(ξ) is the polynomial error estimate
    - ŝ(ξ) is the prediction uncertainty
    - PDF(ξ) is the probability density
    """
    def __init__(self, model, likelihood, bounds, scaler_x, scaler_y):
        # Remove grad_weight and dist_weight as they're not in the paper
        super().__init__(model, likelihood, bounds, scaler_x, scaler_y)
        self.model_2theta = self._create_2theta_model()
        
    def _create_2theta_model(self):
        """Create a model with doubled lengthscale for polynomial error estimation"""
        device = next(self.model.parameters()).device
        model_2theta = type(self.model)(
            self.model.train_inputs[0],
            self.model.train_targets,
            self.likelihood
        ).to(device)
        
        # Double the lengthscale as specified in the paper
        for param_name, param in self.model.named_parameters():
            if 'lengthscale' in param_name:
                corresponding_param = dict(model_2theta.named_parameters())[param_name]
                with torch.no_grad():
                    corresponding_param.copy_(2.0 * param)
        
        model_2theta.eval()
        return model_2theta
        
    def _compute_gradient(self, X):
        """Compute gradient of the GP prediction"""
        device = next(self.model.parameters()).device
        X_tensor = X.clone().detach().requires_grad_(True) # Enable gradient tracking
        
        with torch.enable_grad():
            pred = self.model(X_tensor)
            mean = pred.mean
            grad = torch.autograd.grad(mean.sum(), X_tensor)[0] # Compute ∂f̂(ξ)/∂ξ
            
        return grad.detach()
        
    def _compute_distance(self, X):
        """Compute minimum distance to training points"""
        device = next(self.model.parameters()).device
        train_X = self.model.train_inputs[0]
        
        # Compute pairwise distances
        distances = torch.cdist(X.detach(), train_X)
        min_distances = distances.min(dim=1)[0]
        
        return min_distances
        
    def _compute_Dj(self, X):
        """Compute polynomial error estimate using different lengthscales"""
        with torch.no_grad():
            pred_normal = self.model(X).mean
            pred_2theta = self.model_2theta(X).mean
            Dj = torch.abs(pred_normal - pred_2theta)
            
        return Dj
        
    def _compute_pdf(self, X):
        """Compute probability density function (assuming normal distribution)"""
        X_numpy = X.detach().cpu().numpy()
        X_unscaled = self.scaler_x.inverse_transform(X_numpy)
        
        # Simple multivariate normal PDF centered at bounds mean
        bounds_mean = np.mean(self.bounds, axis=1)
        bounds_std = (self.bounds[:, 1] - self.bounds[:, 0]) / 4  # Using quarter range as std
        
        pdf = np.prod([
            norm.pdf(X_unscaled[:, i], bounds_mean[i], bounds_std[i])
            for i in range(X_unscaled.shape[1])
        ], axis=0)
        
        return torch.tensor(pdf, device=X.device)
    

    def evaluate(self, X):
        """
        Evaluate Criterion 3 exactly as specified in paper:
        Crit(ξ) = (|∂f̂(ξ)/∂ξ|Δ(ξ) + Dj(ξ))ŝ(ξ)PDF(ξ)
        """
        self.model.eval()
        self.likelihood.eval()
        
        device = next(self.model.parameters()).device
        X = torch.tensor(X, dtype=torch.float32).to(device)
        
        # Get prediction uncertainty (ŝ(ξ))
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            pred = self.likelihood(self.model(X))
            uncertainty = pred.variance.sqrt()
        
        # Compute gradient magnitude |∂f̂(ξ)/∂ξ|
        gradient = self._compute_gradient(X)
        gradient_norm = torch.norm(gradient, dim=1)
        
        # Compute distance to nearest sample Δ(ξ)
        distance = self._compute_distance(X)
        
        # Compute polynomial error Dj(ξ)
        Dj = self._compute_Dj(X)
        
        # Compute PDF(ξ)
        pdf = self._compute_pdf(X)
        
        # Combine exactly as in paper's formula:
        # Crit(ξ) = (|∂f̂(ξ)/∂ξ|Δ(ξ) + Dj(ξ))ŝ(ξ)PDF(ξ)
        acquisition_value = (gradient_norm * distance + Dj) * uncertainty * pdf
        
        return -acquisition_value.detach().cpu().numpy()



class ExplorationEnhancedEI(AcquisitionFunction):
    def __init__(self, model, likelihood, bounds, scaler_x, scaler_y, y_train, 
                 n_weights: int = 50, n_samples: int = 10):
        super().__init__(model, likelihood, bounds, scaler_x, scaler_y)
        self.y_train = y_train
        self.V = n_weights
        self.M = n_samples
        self.d = bounds.shape[0]
        self.y_min = torch.min(model.train_targets)
        
    def _generate_random_weights(self) -> Tuple[torch.Tensor, float]:
        device = next(self.model.parameters()).device
        b = np.random.uniform(0, 2 * np.pi)
        W = np.random.normal(0, 1, size=(self.V, self.d))
        W = torch.tensor(W, dtype=torch.float32).to(device)
        return W, b
        
    def _compute_features(self, X: torch.Tensor, W: torch.Tensor, b: float) -> torch.Tensor:
        Wx_b = torch.mm(X, W.t()) + b
        sqrt_term = np.sqrt(2/self.V)
        cos_terms = torch.cos(Wx_b)
        sin_terms = torch.sin(Wx_b)
        phi = sqrt_term * torch.cat([cos_terms, sin_terms], dim=1)
        return phi
        
    def _generate_thompson_sample(self, X: torch.Tensor) -> torch.Tensor:
        W, b = self._generate_random_weights()
        X_train = self.model.train_inputs[0]
        phi_train = self._compute_features(X_train, W, b)
        phi_X = self._compute_features(X, W, b)
        
        sigma2 = self.likelihood.noise.item()
        K = torch.mm(phi_train, phi_train.t()) + sigma2 * torch.eye(len(X_train)).to(X.device)
        K_star = torch.mm(phi_X, phi_train.t())
        
        y_train_scaled = self.model.train_targets
        weights = torch.linalg.solve(K, y_train_scaled)
        g_x = torch.mm(K_star, weights.unsqueeze(1)).squeeze()
        return g_x

    def _compute_ei(self, mean: torch.Tensor, sigma: torch.Tensor, g_star: torch.Tensor) -> torch.Tensor:
        z = (self.y_min - g_star) / (sigma + 1e-9)
        cdf = torch.distributions.Normal(0, 1).cdf(z)
        pdf = torch.distributions.Normal(0, 1).log_prob(z).exp()
        ei = (self.y_min - g_star) * cdf + sigma * pdf
        return ei
        
    def evaluate(self, X: torch.Tensor) -> np.ndarray:
        self.model.eval()
        self.likelihood.eval()
        
        device = next(self.model.parameters()).device
        X = torch.tensor(X, dtype=torch.float32).to(device)
        
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            pred = self.likelihood(self.model(X))
            mu_x = pred.mean
            sigma_x = pred.variance.sqrt()
            
        thompson_samples = []
        expected_improvements = []
        
        for _ in range(self.M):
            g_star = self._generate_thompson_sample(X)
            ei = self._compute_ei(mu_x, sigma_x, g_star)
            expected_improvements.append(ei)
            
        expected_improvements = torch.stack(expected_improvements)
        
        acq_value = torch.where(
            sigma_x > 0,
            expected_improvements.mean(dim=0),
            torch.zeros_like(mu_x)
        )
        
        return -acq_value.cpu().numpy()








class AcquisitionOptimizationProblem(Problem):
    def __init__(self, acquisition_function, n_vars, bounds, scaler_x):
        super().__init__(
            n_var=n_vars,
            n_obj=1,
            n_constr=0,
            xl=scaler_x.transform([np.array([r[0] for r in bounds])])[0],
            xu=scaler_x.transform([np.array([r[1] for r in bounds])])[0]
        )
        self.acquisition_function = acquisition_function

    def _evaluate(self, X, out, *args, **kwargs):
        out["F"] = self.acquisition_function.evaluate(X)


# Update the create_acquisition_function to include E³I
def create_acquisition_function(name: str, model, likelihood, bounds, scaler_x, scaler_y, y_train=None, **kwargs):
    if name.lower() == "e3i":
        return ExplorationEnhancedEI(model, likelihood, bounds, scaler_x, scaler_y, y_train, **kwargs)
    elif name.lower() == "ei":
        return ExpectedImprovement(model, likelihood, bounds, scaler_x, scaler_y, y_train, **kwargs)
    elif name.lower() == "eigf":
        return ExpectedImprovementGlobalFit(model, likelihood, bounds, scaler_x, scaler_y)
    elif name.lower() == "pi":
        return ProbabilityImprovement(model, likelihood, bounds, scaler_x, scaler_y, y_train, **kwargs)
    elif name.lower() == "variance":
        return PredictiveVariance(model, likelihood, bounds, scaler_x, scaler_y)
    elif name.lower() == "lcb":
        return LowerConfidenceBound(model, likelihood, bounds, scaler_x, scaler_y, **kwargs)
    elif name.lower() == "cri3":
        return Criterion3(model, likelihood, bounds, scaler_x, scaler_y)
    else:
        raise ValueError(f"Unknown acquisition function: {name}")


def propose_location(acquisition_name: str, model, likelihood, y_train, bounds, scaler_x, scaler_y, **kwargs):
    acquisition = create_acquisition_function(
        acquisition_name, model, likelihood, bounds, scaler_x, scaler_y, y_train, **kwargs
    )
    return acquisition.optimize()


def append_infill_data_to_file(X_next: np.ndarray, 
                              y_next: np.ndarray, 
                              variable_names: List[str], 
                              save_dir: str = 'RESULT_MODEL_GPR'):
    """Append new evaluation points to the infill data file.
    
    Args:
        X_next: Input points (n_points x n_dimensions)
        y_next: Evaluated values (n_points x 1)
        variable_names: Names of input variables
        save_dir: Directory to save results (default: 'RESULT_MODEL_GPR')
    
    Example:
        >>> X_next = np.array([[1.0, 2.0]])
        >>> y_next = np.array([[3.0]])
        >>> var_names = ['x1', 'x2']
        >>> append_infill_data_to_file(X_next, y_next, var_names)
    """
    # Create directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    infill_file_path = os.path.join(save_dir, 'infill_samples.csv')
    
    # Create DataFrame with new points
    infill_data = {name: X_next[:, i] for i, name in enumerate(variable_names)}
    infill_data['y'] = y_next.flatten()
    df_infill = pd.DataFrame(infill_data)
    
    # Add timestamp column for tracking
    df_infill['timestamp'] = pd.Timestamp.now()
    
    # Save to file (create new or append)
    if not os.path.exists(infill_file_path):
        df_infill.to_csv(infill_file_path, index=False)
    else:
        df_infill.to_csv(infill_file_path, mode='a', header=False, index=False)