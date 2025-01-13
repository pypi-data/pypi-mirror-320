import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image
import torch
import gpytorch
from typing import List, Optional, Dict, Any
from matplotlib import rcParams



# Create plots
rcParams['font.family'] = 'Serif'
rcParams['font.serif'] = 'Times New Roman'
rcParams['font.size'] = 18
rcParams['axes.titlesize'] = 18
rcParams['axes.labelsize'] = 18
rcParams['xtick.labelsize'] = 18
rcParams['ytick.labelsize'] = 18


class EGOAnimator:
    def __init__(self, save_dir: str = 'RESULT_MODEL_GPR/animation', frame_duration: int = 500):
        self.save_dir = save_dir
        self.frames_dir = f'{save_dir}/frames'
        self.frames = []  # Initialize frames list
        self.frame_duration = frame_duration
        os.makedirs(self.frames_dir, exist_ok=True)
        self.device = torch.device('cpu')  # Always use CPU for visualization

    def _prepare_model_for_prediction(self, model, likelihood):
        """Prepare model and likelihood for prediction on CPU."""
        model = model.cpu()
        likelihood = likelihood.cpu()
        model.eval()
        likelihood.eval()
        return model, likelihood

    def _batch_predict(self, model, likelihood, X_batch, scaler_x, scaler_y):
        """Make predictions for a batch of points."""
        X_scaled = scaler_x.transform(X_batch)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
        
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            predictions = likelihood(model(X_tensor))
            mean = predictions.mean.numpy()
            std = predictions.variance.sqrt().numpy() if hasattr(predictions, 'variance') else None
            
        return mean, std

    def save_2D_frame(self,
                    model: gpytorch.models.ExactGP,
                    likelihood: gpytorch.likelihoods.GaussianLikelihood,
                    X_train: np.ndarray,
                    y_train: np.ndarray,
                    scaler_x: object,
                    scaler_y: object,
                    bounds: np.ndarray,
                    iteration: int,
                    variable_names: List[str],
                    n_initial_samples: int,
                    n_points: int = 50,
                    batch_size: int = 1000,
                    device: torch.device = None):  # device parameter ignored
        """Save a 2D visualization frame with memory-efficient computation."""
        frame_path = os.path.join(self.frames_dir, f'frame_{iteration:04d}.png')
        
        try:
            # Prepare model for prediction
            model, likelihood = self._prepare_model_for_prediction(model, likelihood)
            
            # Create mesh grid
            x1 = np.linspace(bounds[0, 0], bounds[0, 1], n_points)
            x2 = np.linspace(bounds[1, 0], bounds[1, 1], n_points)
            X1, X2 = np.meshgrid(x1, x2)
            X_test = np.vstack((X1.flatten(), X2.flatten())).T
            
            # Process predictions in batches
            mean_predictions = np.zeros(len(X_test))
            
            for i in range(0, len(X_test), batch_size):
                batch_end = min(i + batch_size, len(X_test))
                X_batch = X_test[i:batch_end]
                
                batch_mean, _ = self._batch_predict(model, likelihood, X_batch, scaler_x, scaler_y)
                mean_predictions[i:batch_end] = batch_mean
            
            # Transform predictions back to original scale
            mean_predictions = scaler_y.inverse_transform(mean_predictions.reshape(-1, 1)).flatten()
            mean_predictions = mean_predictions.reshape(n_points, n_points)
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 8))
            cf = ax.contourf(X1, X2, mean_predictions, levels=20, cmap='jet')
            
            # Plot samples
            ax.scatter(X_train[:n_initial_samples, 0], X_train[:n_initial_samples, 1], 
                    c='black', s=70, label='Initial samples')
            
            if len(X_train) > n_initial_samples:
                ax.scatter(X_train[n_initial_samples:-1, 0], X_train[n_initial_samples:-1, 1],
                        c='white', s=70, edgecolors='black', label='Added samples')
            
            ax.scatter(X_train[-1, 0], X_train[-1, 1], c='red', s=80, label='Latest sample')
            
            ax.set_xlabel(variable_names[0])
            ax.set_ylabel(variable_names[1])
            ax.set_title(f'Model Prediction - Iteration {iteration}')
            plt.colorbar(cf, label='Predicted Value')
            ax.legend(loc='upper right')
            
            plt.tight_layout()
            plt.savefig(frame_path, facecolor='white', edgecolor='none', 
                       bbox_inches='tight', dpi=150)
            plt.close()
            
            self.frames.append(frame_path)
            
        except Exception as e:
            print(f"Error in save_2D_frame: {str(e)}")
            plt.close()
            raise
            
        finally:
            # Clean up
            torch.cuda.empty_cache() if torch.cuda.is_available() else None


    def save_1D_frame(self, 
                        model: gpytorch.models.ExactGP,
                        likelihood: gpytorch.likelihoods.GaussianLikelihood,
                        X_train: np.ndarray,
                        y_train: np.ndarray,
                        scaler_x: object,
                        scaler_y: object,
                        bounds: np.ndarray,
                        iteration: int,
                        variable_names: List[str],
                        device: torch.device = None,  # device parameter ignored
                        true_function: Optional[callable] = None,
                        batch_size: int = 1000):
        """Save a 1D visualization frame with memory-efficient computation."""
        frame_path = os.path.join(self.frames_dir, f'frame_{iteration:04d}.png')
        
        try:
            # Prepare model for prediction
            model, likelihood = self._prepare_model_for_prediction(model, likelihood)
            
            # Generate test points
            X_test = np.linspace(bounds[0, 0], bounds[0, 1], 200).reshape(-1, 1)
            
            # Initialize arrays for predictions
            mean_predictions = np.zeros(len(X_test))
            std_predictions = np.zeros(len(X_test))
            
            # Process predictions in batches
            for i in range(0, len(X_test), batch_size):
                batch_end = min(i + batch_size, len(X_test))
                X_batch = X_test[i:batch_end]
                
                batch_mean, batch_std = self._batch_predict(model, likelihood, X_batch, scaler_x, scaler_y)
                mean_predictions[i:batch_end] = batch_mean
                std_predictions[i:batch_end] = batch_std if batch_std is not None else 0
            
            # Transform predictions back to original scale
            mean_predictions = scaler_y.inverse_transform(mean_predictions.reshape(-1, 1)).flatten()
            std_predictions = std_predictions.reshape(-1, 1) * scaler_y.scale_
            
            # Create the plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
            fig.suptitle(f'Model Prediction and Acquisition Function - Iteration {iteration}', fontsize=14)
            
            # Plot prediction with uncertainty
            ax1.plot(X_test, mean_predictions, 'b-', label='Prediction', linewidth=2)
            ax1.fill_between(X_test.flatten(), 
                        (mean_predictions - 2 * std_predictions).flatten(), 
                        (mean_predictions + 2 * std_predictions).flatten(), 
                        color='b', alpha=0.2, label='95% Confidence')
            
            ax1.scatter(X_train, y_train, c='r', marker='o', label='Training Points', zorder=5, s=50)
            
            if iteration > 0:
                ax1.scatter(X_train[-1:], y_train[-1:], c='g', marker='*', s=200, 
                        label='Latest Point', zorder=6)
            
            if true_function is not None and callable(true_function):
                try:
                    y_true = true_function(X_test)
                    ax1.plot(X_test, y_true, 'g--', label='True Function', linewidth=2)
                except Exception as e:
                    print(f"Warning: Error plotting true function - {str(e)}")
            
            ax1.set_xlabel(variable_names[0])
            ax1.set_ylabel('Response')
            ax1.legend(fontsize=10)
            ax1.grid(True, alpha=0.3)
            
            # Plot uncertainty
            ax2.plot(X_test, std_predictions, 'r-', label='Uncertainty', linewidth=2)
            if iteration > 0:
                ax2.axvline(X_train[-1], color='g', linestyle='--', alpha=0.5)
            ax2.set_xlabel(variable_names[0])
            ax2.set_ylabel('Prediction Uncertainty')
            ax2.legend(fontsize=10)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(frame_path, bbox_inches='tight', dpi=150)
            plt.close()
            
            self.frames.append(frame_path)
            
        except Exception as e:
            print(f"Error in save_1D_frame: {str(e)}")
            plt.close()
            raise
            
        finally:
            # Clean up
            torch.cuda.empty_cache() if torch.cuda.is_available() else None


    def create_gif(self, duration: Optional[int] = None):
        """Create GIF animation from saved frames with error handling.
        
        Args:
            duration: Duration for each frame in milliseconds. If None, uses default frame_duration
        """
        try:
            if not self.frames:
                print("No frames found to create animation")
                return
                
            # Use provided duration or default
            gif_duration = duration if duration is not None else self.frame_duration
            
            frames = []
            for frame_path in sorted(self.frames):
                if os.path.exists(frame_path):
                    try:
                        frames.append(Image.open(frame_path))
                    except Exception as e:
                        print(f"Warning: Could not open frame {frame_path}: {str(e)}")
                        continue
            
            if frames:
                output_path = os.path.join(self.save_dir, 'optimization_progress.gif')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                try:
                    frames[0].save(
                        output_path,
                        save_all=True,
                        append_images=frames[1:],
                        duration=gif_duration,
                        loop=0
                    )
                    print(f"Animation saved to {output_path} with frame duration {gif_duration}ms")
                except Exception as e:
                    print(f"Error saving animation: {str(e)}")
            else:
                print("No valid frames found to create animation")
                
        except Exception as e:
            print(f"Error creating animation: {str(e)}")






class ModelVisualizer:
    """Handles final model visualization and assessment."""
    def __init__(self, model, likelihood, scaler_x, scaler_y, bounds, variable_names, history,
                 device, save_dir='RESULT_MODEL_GPR'):
        self.model = model
        self.likelihood = likelihood
        self.scaler_x = scaler_x
        self.scaler_y = scaler_y
        self.bounds = bounds
        self.variable_names = variable_names
        self.device = device
        self.history = history
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # Ensure model and likelihood are on the correct device
        self.model = self.model.to(self.device)
        self.likelihood = self.likelihood.to(self.device)
    
    def predict(self, X):
        """Make predictions with the model."""
        self.model.eval()
        self.likelihood.eval()
        
        X_scaled = self.scaler_x.transform(X)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(self.device)
        
        with torch.no_grad(), gpytorch.settings.fast_pred_var():
            predictions = self.likelihood(self.model(X_tensor))
            mean = predictions.mean.cpu().numpy()
            std = predictions.variance.sqrt().cpu().numpy()
            
        mean = self.scaler_y.inverse_transform(mean.reshape(-1, 1))
        std = std.reshape(-1, 1) * self.scaler_y.scale_
        
        return mean, std
    
            
    def _plot_1D_final(self, X_train, y_train, true_function=None, n_points=200):
        """Create final 1D prediction plot."""
        plt.figure(figsize=(12, 8))
        
        # Generate test points
        X_test = np.linspace(self.bounds[0, 0], self.bounds[0, 1], n_points).reshape(-1, 1)
        mean, std = self.predict(X_test)
        
        plt.plot(X_test, mean, 'b-', label='Prediction', linewidth=2)
        plt.fill_between(X_test.flatten(), 
                        (mean - 2 * std).flatten(), 
                        (mean + 2 * std).flatten(), 
                        color='b', alpha=0.2, label='95% Confidence')
        
        plt.scatter(X_train, y_train, c='r', marker='o', label='Training Points')
        
        if true_function is not None:
            y_true = true_function(X_test)
            plt.plot(X_test, y_true, 'g--', label='True Function')
        
        plt.xlabel(self.variable_names[0])
        plt.ylabel('Response')
        plt.title('Final Model Prediction')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.savefig(f'{self.save_dir}/final_prediction_1d.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_final_prediction(self, X_train, y_train, true_function=None):
        """Create final prediction plots."""
        if len(self.variable_names) == 1:
            self._plot_1D_final(X_train, y_train, true_function)
        elif len(self.variable_names) == 2:
            self._plot_2D_final(X_train, y_train)

    def _plot_2D_final(self, X_train, y_train, n_points=50):
        """Create final 2D prediction plot."""
        x1 = np.linspace(self.bounds[0, 0], self.bounds[0, 1], n_points)
        x2 = np.linspace(self.bounds[1, 0], self.bounds[1, 1], n_points)
        X1, X2 = np.meshgrid(x1, x2)
        X_test = np.vstack((X1.flatten(), X2.flatten())).T
        
        mean, std = self.predict(X_test)
        Y_pred = mean.reshape(n_points, n_points)
        Y_std = std.reshape(n_points, n_points)
        
        fig = plt.figure(figsize=(20, 8))
        
        # Prediction surface
        ax1 = fig.add_subplot(121, projection='3d')
        surf1 = ax1.plot_surface(X1, X2, Y_pred, cmap='viridis')
        ax1.scatter(X_train[:, 0], X_train[:, 1], y_train, c='r', marker='o')
        
        ax1.set_xlabel(self.variable_names[0])
        ax1.set_ylabel(self.variable_names[1])
        ax1.set_zlabel('Response')
        ax1.set_title('Final Prediction Surface')
        plt.colorbar(surf1, ax=ax1)
        
        # Uncertainty surface
        ax2 = fig.add_subplot(122, projection='3d')
        surf2 = ax2.plot_surface(X1, X2, Y_std, cmap='magma')
        ax2.scatter(X_train[:, 0], X_train[:, 1], np.zeros_like(y_train), c='r', marker='o')
        
        ax2.set_xlabel(self.variable_names[0])
        ax2.set_ylabel(self.variable_names[1])
        ax2.set_zlabel('Uncertainty (std)')
        ax2.set_title('Final Prediction Uncertainty')
        plt.colorbar(surf2, ax=ax2)
        
        plt.tight_layout()
        plt.savefig(f'{self.save_dir}/final_prediction_2d.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_convergence_metrics(self, history: dict):
        """Plot optimization metrics over iterations."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        iterations = history['iterations']
        
        # Plot RMSE evolution
        ax1.plot(iterations, history['rmse_values'], 'r-', linewidth=2)
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('RMSE')
        ax1.set_title('RMSE Evolution')
        ax1.grid(True, alpha=0.3)
        
        # Plot uncertainty evolution
        ax2.plot(iterations, history['mean_uncertainty'], 'g-', linewidth=2)
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Mean Uncertainty')
        ax2.set_title('Uncertainty Evolution')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.save_dir}/convergence_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()


    def plot_error_analysis(self, X_train, y_train):
        """Plot prediction errors and residuals."""
        # Get predictions for training points
        y_pred, y_std = self.predict(X_train)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Actual vs Predicted
        ax1.scatter(y_train, y_pred, c='b', alpha=0.5)
        ax1.plot([y_train.min(), y_train.max()], [y_train.min(), y_train.max()], 'r--')
        ax1.set_xlabel('Actual Values')
        ax1.set_ylabel('Predicted Values')
        ax1.set_title('Actual vs Predicted')
        ax1.grid(True, alpha=0.3)
        
        # Residuals
        residuals = y_train - y_pred
        ax2.scatter(y_pred, residuals, c='b', alpha=0.5)
        ax2.axhline(y=0, color='r', linestyle='--')
        ax2.set_xlabel('Predicted Values')
        ax2.set_ylabel('Residuals')
        ax2.set_title('Residuals vs Predicted')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.save_dir}/error_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()


    def create_complete_visualization(self, X_train, y_train, history, true_function=None):
        """Create all visualizations."""
        print("Creating final model visualizations...")
        try:
            self.plot_final_prediction(X_train, y_train, true_function)
            self.plot_error_analysis(X_train, y_train)
            self.plot_convergence_metrics(history)
            print(f"All visualizations saved in {self.save_dir}")
        except Exception as e:
            print(f"Error during visualization: {str(e)}")
            










