import torch
import gpytorch
import joblib
import json
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Dict, List, Tuple, Optional

# Rich progress bar imports
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.progress import TimeRemainingColumn, TimeElapsedColumn, SpinnerColumn
from rich.console import Console
from rich.panel import Panel
import platform

# Suppress warnings
import warnings
from gpytorch.utils.warnings import GPInputWarning, NumericalWarning
warnings.filterwarnings("ignore", category=GPInputWarning)
warnings.filterwarnings("ignore", category=NumericalWarning)

class GPRegressionModel(gpytorch.models.ExactGP):
    """Gaussian Process Regression Model."""
    def __init__(self, train_x: torch.Tensor, train_y: torch.Tensor, 
                 likelihood: gpytorch.likelihoods.Likelihood):
        super().__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(
            gpytorch.kernels.MaternKernel(
                nu=2.5,
                ard_num_dims=train_x.size(-1)
            )
        )
        
        # Initial Hyperparameters
        self.covar_module.base_kernel.lengthscale = 1.0
        self.covar_module.outputscale = 1.0
        self.likelihood.noise_covar.noise = 1e-4

    def forward(self, x: torch.Tensor) -> gpytorch.distributions.MultivariateNormal:
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultivariateNormal(mean_x, covar_x)

class MetaTraining:
    """
    MetaTraining: A class for training Gaussian Process Regression models.
    
    Default Settings:
    ----------------
    test_size : float = 0.3
        Fraction of data used for testing (default: 30% testing, 70% training)
    
    num_iterations : int = 100
        Maximum number of training iterations
        Early stopping may end training earlier if no improvement is seen
    
    prefer_gpu : bool = True
        If True, uses GPU when available
        If False or GPU unavailable, uses CPU
    
    show_progress : bool = True
        If True, shows training progress bar and loss values
        If False, trains silently
    
    show_hardware_info : bool = True
        If True, displays system information (CPU/GPU, memory, etc.)
        If False, hides hardware details
    
    show_model_info : bool = True
        If True, shows model architecture and training setup
        If False, hides model details
    
    output_dir : str = 'RESULT_MODEL_GPR'
        Directory where results will be saved:
        - Trained model (gpr_model.pth)
        - Data scalers (scaler_X.pkl, scaler_y.pkl)
        - Performance plots
    
    data_dir : str = 'DATA_PREPARATION'
        Directory where input data is located
        Required files when using default data:
        - data_info.json
        - training_data.csv

    Usage Examples:
    --------------
    1. Basic usage with all defaults:
        meta = MetaTraining()
        model = meta.train('training_data.csv')
    
    2. Custom settings for minimal output:
        meta = MetaTraining(
            test_size=0.2,             # 20% testing, 80% training
            num_iterations=200,         # Maximum 200 iterations
            prefer_gpu=False,           # Force CPU usage
            show_progress=True,         # Show training progress
            show_hardware_info=False,   # Hide hardware details
            show_model_info=False,      # Hide model architecture
            output_dir='my_results'     # Custom save directory
        )
    
    3. Using custom data:
        X = your_feature_data          # numpy array or pandas DataFrame
        y = your_target_values         # numpy array
        meta = MetaTraining()
        model = meta.train(X, y, custom_data=True)
    
    4. Making predictions:
        predictions, uncertainties = meta.predict(X_new)
    
    Output Files:
    ------------
    The following files are saved in output_dir:
    - gpr_model.pth: Trained PyTorch model
    - scaler_X.pkl: Feature scaler
    - scaler_y.pkl: Target scaler
    - performance/model_performance.png: Performance plots
    """
    
    def __init__(self,
                 test_size: float = 0.3,
                 num_iterations: int = 100,
                 prefer_gpu: bool = True,
                 show_progress: bool = True,
                 show_hardware_info: bool = True,
                 show_model_info: bool = True,
                 output_dir: str = 'RESULT_MODEL_GPR',
                 data_dir: str = 'DATA_PREPARATION'):
        """
        Initialize MetaTraining with configuration.
        
        Args:
            test_size: Fraction of data to use for testing (default: 0.3)
            num_iterations: Number of training iterations (default: 100)
            prefer_gpu: Whether to use GPU if available (default: True)
            show_progress: Whether to show detailed progress (default: True)
            output_dir: Directory for saving results (default: 'RESULT_MODEL_GPR')
            data_dir: Directory containing input data (default: 'DATA_PREPARATION')
        """
        self.test_size = test_size
        self.num_iterations = num_iterations
        self.show_progress = show_progress
        self.output_dir = output_dir
        self.data_dir = data_dir
        self.show_hardware_info = show_hardware_info
        self.show_model_info = show_model_info
        
        # Setup device
        self.device = torch.device("cuda" if torch.cuda.is_available() and prefer_gpu else "cpu")
        self.console = Console()
        
        # Initialize model components
        self.model = None
        self.likelihood = None
        self.scaler_X = None
        self.scaler_y = None

    def print_device_info(self):
        """Print information about the computing device being used."""
        if self.device.type == "cuda":
            device_name = torch.cuda.get_device_name(0)
            memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            cuda_version = torch.version.cuda
            
            self.console.print("\n[green]Hardware Configuration[/green]")
            self.console.print(f"[white]• Device:[/white] GPU - {device_name}")
            self.console.print(f"[white]• GPU Memory:[/white] {memory_gb:.1f} GB")
            self.console.print(f"[white]• CUDA Version:[/white] {cuda_version}")
        else:
            import psutil
            device_name = platform.processor() or "Unknown CPU"
            memory_gb = psutil.virtual_memory().total / 1024**3
            cpu_cores = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else "Unknown"
            
            self.console.print("\n[green]Hardware Configuration[/green]")
            self.console.print(f"[white]• Device:[/white] CPU - {device_name}")
            self.console.print(f"[white]• CPU Cores:[/white] {cpu_cores}")
            self.console.print(f"[white]• CPU Frequency:[/white] {cpu_freq:.2f} MHz" if isinstance(cpu_freq, (int, float)) else f"[white]• CPU Frequency:[/white] {cpu_freq}")
            self.console.print(f"[white]• System Memory:[/white] {memory_gb:.1f} GB")
        
        self.console.print(f"[white]• PyTorch Version:[/white] {torch.__version__}")
        self.console.print(f"[white]• GPyTorch Version:[/white] {gpytorch.__version__}")
        self.console.print(f"[white]• NumPy Version:[/white] {np.__version__}")
        self.console.print(f"[white]• Operating System:[/white] {platform.system()} {platform.version()}\n")

    def train(self, X, y=None, custom_data=False):
        """
        Train the GPR model.
        
        Args:
            X: Features or path to training_data.csv if custom_data=False
            y: Target values (only needed if custom_data=True)
            custom_data: Whether using custom data instead of loading from file
        """
        if not custom_data:
            # Load data from files
            data_info_path = os.path.join(self.data_dir, 'data_info.json')
            data_path = os.path.join(self.data_dir, 'training_data.csv')
            
            if not os.path.exists(data_info_path) or not os.path.exists(data_path):
                raise FileNotFoundError(f"Required files not found in {self.data_dir}")
            
            with open(data_info_path, 'r') as f:
                data_info = json.load(f)
            
            variables = data_info['variables']
            self.variable_names = [var['name'] for var in variables]
            
            data = pd.read_csv(data_path)
            X = data[self.variable_names].values
            y = data['y'].values.reshape(-1, 1)
        else:
            if y is None:
                raise ValueError("Target values 'y' must be provided when custom_data=True")
            if isinstance(X, pd.DataFrame):
                self.variable_names = X.columns.tolist()
                X = X.values
            else:
                self.variable_names = [f'X{i}' for i in range(X.shape[1])]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size)
        
        # Print information if enabled
        if self.show_hardware_info:
            self.print_device_info()
        if self.show_model_info:
            self.print_model_info(X_train.shape)
        
        # Scale data
        self.scaler_X = StandardScaler().fit(X_train)
        self.scaler_y = StandardScaler().fit(y_train)

        X_train_scaled = self.scaler_X.transform(X_train)
        y_train_scaled = self.scaler_y.transform(y_train)
        X_test_scaled = self.scaler_X.transform(X_test)
        y_test_scaled = self.scaler_y.transform(y_test)

        # Convert to tensors
        X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32).to(self.device)
        y_train_tensor = torch.tensor(y_train_scaled.flatten(), dtype=torch.float32).to(self.device)
        X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32).to(self.device)
        y_test_tensor = torch.tensor(y_test_scaled.flatten(), dtype=torch.float32).to(self.device)

        # Initialize model
        self.likelihood = gpytorch.likelihoods.GaussianLikelihood().to(self.device)
        self.model = GPRegressionModel(X_train_tensor, y_train_tensor, self.likelihood).to(self.device)

        # Training
        self.model.train()
        self.likelihood.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.1)
        mll = gpytorch.mlls.ExactMarginalLogLikelihood(self.likelihood, self.model)

        # Training loop with progress bar
        if self.show_progress:
            self._train_with_progress(optimizer, mll, X_train_tensor, y_train_tensor)
        else:
            self._train_without_progress(optimizer, mll, X_train_tensor, y_train_tensor)

        # Evaluate and save
        self._evaluate_and_save(X_train, y_train, X_test, y_test)
        
        return self.model, self.scaler_X, self.scaler_y

    def _train_with_progress(self, optimizer, mll, X_train_tensor, y_train_tensor):
        """Training loop with progress bar."""
        best_loss = float('inf')
        patience = 20
        patience_counter = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TextColumn("[cyan]{task.fields[loss]}"),
            TextColumn("[magenta]{task.fields[best_loss]}"),
        ) as progress:
            task = progress.add_task(
                "[cyan]Training GPR",
                total=self.num_iterations,
                loss="Loss: N/A",
                best_loss="Best: N/A"
            )

            with gpytorch.settings.cholesky_jitter(1e-3):
                for i in range(self.num_iterations):
                    current_loss = self._train_step(optimizer, mll, X_train_tensor, y_train_tensor)
                    
                    if current_loss < best_loss:
                        best_loss = current_loss
                        patience_counter = 0
                    else:
                        patience_counter += 1
                    
                    progress.update(
                        task,
                        advance=1,
                        loss=f"Loss: {current_loss:.4f}",
                        best_loss=f"Best: {best_loss:.4f}"
                    )
                    
                    if patience_counter >= patience:
                        progress.stop()
                        self.console.print("\n[yellow]Early stopping triggered[/yellow]")
                        break

    def _train_without_progress(self, optimizer, mll, X_train_tensor, y_train_tensor):
        """Training loop without progress bar."""
        best_loss = float('inf')
        patience = 20
        patience_counter = 0
        
        with gpytorch.settings.cholesky_jitter(1e-3):
            for i in range(self.num_iterations):
                current_loss = self._train_step(optimizer, mll, X_train_tensor, y_train_tensor)
                
                if current_loss < best_loss:
                    best_loss = current_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    
                if patience_counter >= patience:
                    break

    def _train_step(self, optimizer, mll, X_train_tensor, y_train_tensor):
        """Single training step."""
        optimizer.zero_grad()
        output = self.model(X_train_tensor)
        loss = -mll(output, y_train_tensor)
        loss.backward()
        optimizer.step()
        return loss.item()

    def _evaluate_and_save(self, X_train, y_train, X_test, y_test):
        """Evaluate model and save results."""
        self.model.eval()
        self.likelihood.eval()
        
        # Save model and scalers
        os.makedirs(self.output_dir, exist_ok=True)
        self._save_model()
        
        # Make predictions and evaluate
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            X_train_tensor = torch.tensor(self.scaler_X.transform(X_train), dtype=torch.float32).to(self.device)
            X_test_tensor = torch.tensor(self.scaler_X.transform(X_test), dtype=torch.float32).to(self.device)
            
            train_preds = self.likelihood(self.model(X_train_tensor))
            test_preds = self.likelihood(self.model(X_test_tensor))
            
            y_train_pred = self.scaler_y.inverse_transform(train_preds.mean.cpu().numpy().reshape(-1, 1))
            y_test_pred = self.scaler_y.inverse_transform(test_preds.mean.cpu().numpy().reshape(-1, 1))
        
        # Calculate metrics
        train_rmse = np.sqrt(((y_train - y_train_pred) ** 2).mean())
        test_rmse = np.sqrt(((y_test - y_test_pred) ** 2).mean())
        R2_train = 1 - ((y_train - y_train_pred) ** 2).mean() / y_train.var()
        R2_test = 1 - ((y_test - y_test_pred) ** 2).mean() / y_test.var()
        
        if self.show_progress:
            self._print_results(train_rmse, test_rmse, R2_train, R2_test)
        
        # Create plots
        self._create_performance_plots(y_train, y_train_pred, y_test, y_test_pred, 
                                     train_rmse, test_rmse, R2_train, R2_test)

    def _save_model(self):
        """Save model and associated data."""
        # Save scalers
        joblib.dump(self.scaler_X, os.path.join(self.output_dir, 'scaler_X.pkl'))
        joblib.dump(self.scaler_y, os.path.join(self.output_dir, 'scaler_y.pkl'))
        
        # Move model to CPU and save
        model_cpu = self.model.cpu()
        likelihood_cpu = self.likelihood.cpu()
        
        state_dict = {
            'model': model_cpu.state_dict(),
            'likelihood': likelihood_cpu.state_dict(),
            'train_inputs': [x.cpu() for x in model_cpu.train_inputs],
            'train_targets': model_cpu.train_targets.cpu(),
            'input_size': model_cpu.train_inputs[0].shape[1]
        }
        
        torch.save(state_dict, os.path.join(self.output_dir, 'gpr_model.pth'))
        
        # Move model back to original device
        self.model = self.model.to(self.device)
        self.likelihood = self.likelihood.to(self.device)

    def print_model_info(self, input_shape):
        """Print information about the model architecture and training setup."""
        self.console.print("\n[green]Model Configuration[/green]")
        self.console.print(f"[white]• Model Type:[/white] Gaussian Process Regression")
        self.console.print(f"[white]• Kernel:[/white] Matérn 2.5 with ARD")
        self.console.print(f"[white]• Input Features:[/white] {input_shape[1]}")
        self.console.print(f"[white]• Training Samples:[/white] {input_shape[0]}")
        self.console.print(f"[white]• Test Size:[/white] {self.test_size * 100:.0f}%")
        self.console.print(f"[white]• Max Iterations:[/white] {self.num_iterations}")
        self.console.print(f"[white]• Optimizer:[/white] Adam")
        self.console.print(f"[white]• Learning Rate:[/white] 0.1")
        self.console.print("[white]• Early Stopping:[/white] Yes (patience=20)")
        
        if hasattr(self, 'variable_names'):
            self.console.print("\n[green]Features:[/green]")
            for i, name in enumerate(self.variable_names, 1):
                self.console.print(f"[white]• {i}. {name}[/white]")
        self.console.print("")

    def _print_results(self, train_rmse, test_rmse, R2_train, R2_test):
        """Print training results."""
        self.console.print("\n[green]Model Performance:[/green]")
        self.console.print(f"[white]• Training RMSE: {train_rmse:.4f}[/white]")
        self.console.print(f"[white]• Testing RMSE: {test_rmse:.4f}[/white]")
        self.console.print(f"[white]• Training R²: {R2_train:.4f}[/white]")
        self.console.print(f"[white]• Testing R²: {R2_test:.4f}[/white]")

    def _create_performance_plots(self, y_train, y_train_pred, y_test, y_test_pred,
                                train_rmse, test_rmse, R2_train, R2_test):
        """Create and save performance plots."""
        plots_dir = os.path.join(self.output_dir, 'performance')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Plot settings
        rcParams['font.family'] = 'Serif'
        rcParams['font.serif'] = 'Times New Roman'
        rcParams['font.size'] = 14
        rcParams['axes.titlesize'] = 16
        rcParams['axes.labelsize'] = 14
        rcParams['xtick.labelsize'] = 14
        rcParams['ytick.labelsize'] = 14

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # Training plot
        ax1.scatter(y_train, y_train_pred, color='blue', alpha=0.5, label='Data points')
        ax1.plot([y_train.min(), y_train.max()], 
                [y_train.min(), y_train.max()], 
                'k--', label='Perfect fit')
        ax1.set_xlabel('True Values')
        ax1.set_ylabel('Predicted Values')
        ax1.set_title(f'Training Data\nR² = {R2_train:.4f}, RMSE = {train_rmse:.4f}')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend()

        # Testing plot
        ax2.scatter(y_test, y_test_pred, color='blue', alpha=0.5, label='Data points')
        ax2.plot([y_test.min(), y_test.max()], 
                [y_test.min(), y_test.max()], 
                'k--', label='Perfect fit')
        ax2.set_xlabel('True Values')
        ax2.set_ylabel('Predicted Values')
        ax2.set_title(f'Testing Data\nR² = {R2_test:.4f}, RMSE = {test_rmse:.4f}')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'model_performance.png'), dpi=300, bbox_inches='tight')
        plt.close()

def predict(self, X):
    """
    Make predictions using the trained model.
    
    Args:
        X: Input features (numpy array or DataFrame)
        
    Returns:
        Predictions and their standard deviations
    """
    if self.model is None:
        raise RuntimeError("Model not trained. Call train() first.")
        
    if isinstance(X, pd.DataFrame):
        X = X.values
        
    self.model.eval()
    self.likelihood.eval()
    
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        X_scaled = self.scaler_X.transform(X)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
        predictions = self.likelihood(self.model(X_tensor))
        
        mean = self.scaler_y.inverse_transform(
            predictions.mean.cpu().numpy().reshape(-1, 1)
        )
        std = predictions.variance.sqrt().cpu().numpy().reshape(-1, 1) * self.scaler_y.scale_
        
    return mean, std


# Example usage
if __name__ == "__main__":

    # Example 1: Basic usage with default settings (shows all information)
    meta = MetaTraining(
        show_hardware_info=True,   # Show hardware details
        show_model_info=True       # Show model architecture
    )
    model, scaler_X, scaler_y = meta.train('training_data.csv')
    
    # Example 2: Custom data with minimal output
    """
    # Create or load your data
    X = pd.DataFrame(...)  # Your feature data
    y = ...  # Your target values
    
    # Initialize with custom settings
    meta = MetaTraining(
        test_size=0.2,             # Use 20% for testing
        num_iterations=200,         # Train for 200 iterations
        prefer_gpu=False,          # Use CPU
        show_progress=True,        # Show training progress
        show_hardware_info=False,  # Hide hardware details
        show_model_info=True,      # Show model architecture
        output_dir='my_results'    # Custom output directory
    )
    
    # Train the model
    model, scaler_X, scaler_y = meta.train(X, y, custom_data=True)
    
    # Make predictions
    X_new = ...  # New data for prediction
    predictions, uncertainties = meta.predict(X_new)
    """