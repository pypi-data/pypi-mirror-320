# adaptive_sampler.py
from scipy.stats import truncnorm
import numpy as np
from typing import List, Dict, Any
from pyDOE import lhs




class AdaptiveDistributionSampler:
    """Simplified sampler with LHS for design variables and direct sampling for env variables"""
    
    @staticmethod
    def generate_samples(distribution, mean=None, cov=None, lower=None, upper=None, size=1000):
        """
        Generate samples with strict boundary enforcement.
        Args:
            distribution: Type of distribution ('normal', 'lognormal', 'uniform')
            mean: Mean value for normal/lognormal
            cov: Coefficient of variation for normal/lognormal
            lower: Lower bound
            upper: Upper bound
            size: Number of samples to generate
        """
        if distribution == 'uniform':
            return np.random.uniform(lower, upper, size)
        
        elif distribution == 'normal':
            # Calculate standard deviation from COV
            std = abs(mean * cov) if mean is not None and cov is not None else 1.0
            
            # Ensure std is positive
            if std <= 0:
                std = 1.0
                
            # Calculate normalized bounds
            a = (lower - mean) / std
            b = (upper - mean) / std
            
            # Generate samples using truncated normal distribution
            samples = truncnorm.rvs(a, b, loc=mean, scale=std, size=size)
            return np.clip(samples, lower, upper)
        
        elif distribution == 'lognormal':
            # Ensure positive values for lognormal parameters
            sigma = np.sqrt(np.log(1 + cov**2))
            mu = np.log(mean) - 0.5 * sigma**2
            
            if lower is not None and upper is not None:
                log_lower = np.log(max(lower, 1e-10))  # Prevent log(0)
                log_upper = np.log(upper)
                a = (log_lower - mu) / sigma
                b = (log_upper - mu) / sigma
                log_samples = truncnorm.rvs(a, b, loc=mu, scale=sigma, size=size)
                samples = np.exp(log_samples)
            else:
                samples = np.random.lognormal(mu, sigma, size)
            
            return np.clip(samples, lower, upper)
        
        else:
            raise ValueError(f"Unsupported distribution: {distribution}")

    @staticmethod
    def generate_design_samples(design_vars: List[Dict[str, Any]], num_samples: int) -> np.ndarray:
        """Generate samples for design variables using LHS"""
        design_bounds = np.array([var['range'] for var in design_vars])
        lhs_samples = lhs(len(design_vars), samples=num_samples)
        design_samples = lhs_samples * (design_bounds[:, 1] - design_bounds[:, 0]) + design_bounds[:, 0]
        return design_samples

    @staticmethod
    def generate_env_samples(var: Dict[str, Any], num_samples: int) -> np.ndarray:
        """Generate samples for a single environmental variable"""
        if var['distribution'] == 'uniform':
            return np.random.uniform(var['low'], var['high'], num_samples)
        elif var['distribution'] in ['normal', 'lognormal']:
            lower = var.get('low', float('-inf'))
            upper = var.get('high', float('inf'))
            return AdaptiveDistributionSampler.generate_samples(
                distribution=var['distribution'],
                mean=var['mean'],
                cov=var['cov'],
                lower=lower,
                upper=upper,
                size=num_samples
            )

    @classmethod
    def generate_all_samples(cls, variables: List[Dict[str, Any]], num_samples: int) -> np.ndarray:
        """Generate samples for all variables"""
        all_samples = np.zeros((num_samples, len(variables)))
        
        # Handle design variables using LHS
        design_vars = [var for var in variables if var['vars_type'] == 'design_vars']
        if design_vars:
            design_samples = cls.generate_design_samples(design_vars, num_samples)
            design_idx = 0
            for i, var in enumerate(variables):
                if var['vars_type'] == 'design_vars':
                    all_samples[:, i] = design_samples[:, design_idx]
                    design_idx += 1
        
        # Handle environmental variables with direct sampling
        for i, var in enumerate(variables):
            if var['vars_type'] == 'env_vars':
                all_samples[:, i] = cls.generate_env_samples(var, num_samples)
        
        return all_samples

    @staticmethod
    def calculate_input_bounds(variables: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Calculate input bounds for all variables
        Args:
            variables: List of variable dictionaries
        Returns:
            List of [lower, upper] bounds for each variable
        """
        bounds = []
        for var in variables:
            if var['vars_type'] == 'design_vars':
                bounds.append(var['range'])
            elif var['vars_type'] == 'env_vars':
                if var['distribution'] == 'uniform':
                    bounds.append([var['low'], var['high']])
                elif var['distribution'] == 'normal':
                    # Use mean ± 3*std for normal distribution
                    std = var['mean'] * var['cov']
                    bounds.append([var['mean'] - 3*std, var['mean'] + 3*std])
                elif var['distribution'] == 'lognormal':
                    # Use log-space bounds for lognormal
                    log_std = np.sqrt(np.log(1 + var['cov']**2))
                    log_mean = np.log(var['mean']) - 0.5 * log_std**2
                    bounds.append([
                        np.exp(log_mean - 3*log_std),
                        np.exp(log_mean + 3*log_std)
                    ])
        return bounds