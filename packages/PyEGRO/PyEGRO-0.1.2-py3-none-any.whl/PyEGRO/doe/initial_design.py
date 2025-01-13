# File: PyEGRO/initial_design.py

from typing import List, Dict, Union, Optional, Callable
import os
import numpy as np
import pandas as pd
import json
from dataclasses import dataclass

from rich.progress import Progress, TextColumn, BarColumn
from rich.progress import TaskProgressColumn, TimeRemainingColumn
from rich.progress import TimeElapsedColumn, SpinnerColumn
from rich.console import Console
from rich.table import Table

from .sampling import AdaptiveDistributionSampler

@dataclass
class Variable:
    """Class to represent a variable in the design space."""
    name: str
    vars_type: str
    distribution: str
    description: str
    
    # For design variables
    range: Optional[List[float]] = None
    cov: Optional[float] = None
    
    # For environmental variables
    mean: Optional[float] = None
    low: Optional[float] = None
    high: Optional[float] = None

class InitialDesign:
    """
    InitialDesign: A class for generating initial design samples with support for 
    both design and environmental variables.

    Display Options:
    --------------
    show_progress : bool = True
        Show progress bar during sample generation and evaluation
        - Progress percentage
        - Current sample number
        - Time elapsed/remaining
    
    show_result : bool = False
        Show final results after completion
        - Summary statistics table
        - File save locations
        - Completion message
    
    Default Settings:
    ----------------
    output_dir : str = 'DATA_PREPARATION'
        Directory where generated data will be saved

    Variable Types and Distributions:
    ------------------------------
    1. Design Variables:
        - Supported distributions: 'normal', 'lognormal'
        - Required parameters:
            * name: Variable name
            * range_bounds: [min, max] bounds
            * cov: Coefficient of variation
            * distribution: Distribution type (default: 'normal')
            * description: Variable description (optional)

    2. Environmental Variables:
        - Supported distributions: 'normal', 'lognormal', 'uniform'
        - Required parameters for normal/lognormal:
            * name: Variable name
            * distribution: Distribution type
            * mean: Mean value
            * cov: Coefficient of variation
            * description: Variable description (optional)
        - Required parameters for uniform:
            * name: Variable name
            * distribution: 'uniform'
            * low: Lower bound
            * high: Upper bound
            * description: Variable description (optional)

    Usage Examples:
    --------------
    # Basic usage
    def objective(x):
        return np.sum(x**2, axis=1)
        
    design = InitialDesign(
        objective_function=objective,
        show_progress=True,    # Show progress bar
        show_result=True       # Show final statistics
    )
    
    # Add variables
    design.add_design_variable(
        name='x1',
        range_bounds=[-5, 5],
        cov=0.1
    )
    
    design.add_env_variable(
        name='env1',
        distribution='normal',
        mean=0.5,
        cov=0.1
    )
    
    # Generate samples
    design.run(num_samples=50)
    """
    
    def __init__(
        self,
        objective_function: Callable,
        output_dir: str = 'DATA_PREPARATION',
        show_progress: bool = False,
        show_result: bool = False
    ):
        """
        Initialize the InitialDesign class.
        
        Args:
            objective_function: Function that takes numpy array of samples and returns objective values
            output_dir: Directory to save output files
            show_progress: Whether to show progress bar during sampling
            show_result: Whether to show final results and statistics
        """
        self.objective_function = objective_function
        self.output_dir = output_dir
        self.show_progress = show_progress
        self.show_result = show_result
        self.variables = []
        os.makedirs(output_dir, exist_ok=True)
        
    def add_design_variable(
        self,
        name: str,
        range_bounds: List[float],
        cov: float,
        distribution: str = 'normal',
        description: str = ''
    ) -> None:
        """
        Add a design variable to the problem.
        
        Args:
            name: Name of the variable
            range_bounds: [min, max] bounds for the variable
            cov: Coefficient of variation
            distribution: Type of distribution ('normal' or 'lognormal')
            description: Description of the variable
        """
        var = {
            'name': name,
            'vars_type': 'design_vars',
            'range': range_bounds,
            'cov': cov,
            'distribution': distribution,
            'description': description
        }
        self.variables.append(var)

    def add_env_variable(
        self,
        name: str,
        distribution: str,
        description: str = '',
        mean: Optional[float] = None,
        cov: Optional[float] = None,
        low: Optional[float] = None,
        high: Optional[float] = None
    ) -> None:
        """
        Add an environmental variable to the problem.
        
        Args:
            name: Name of the variable
            distribution: Type of distribution ('normal', 'lognormal', or 'uniform')
            description: Description of the variable
            mean: Mean value (for normal and lognormal distributions)
            cov: Coefficient of variation (for normal and lognormal distributions)
            low: Lower bound (for uniform distribution)
            high: Upper bound (for uniform distribution)
        """
        var = {
            'name': name,
            'vars_type': 'env_vars',
            'distribution': distribution,
            'description': description
        }
        
        if distribution in ['normal', 'lognormal']:
            if mean is None or cov is None:
                raise ValueError(f"{distribution} distribution requires mean and cov")
            var['mean'] = mean
            var['cov'] = cov
        elif distribution == 'uniform':
            if low is None or high is None:
                raise ValueError("Uniform distribution requires low and high bounds")
            var['low'] = low
            var['high'] = high
        else:
            raise ValueError(f"Unsupported distribution: {distribution}")
            
        self.variables.append(var)

    def generate_samples(self, num_samples: int) -> pd.DataFrame:
        """Generate samples and evaluate objective function."""
        sampler = AdaptiveDistributionSampler()
        print('\n')

        # Create progress context
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TextColumn("[cyan]{task.fields[info]}"),
            disable=not self.show_progress
        ) as progress:
            
            # First task: Generate samples
            task1 = progress.add_task(
                "[white]Generating design points...",
                total=1,
                info="Sampling..."
            )
            
            all_samples = sampler.generate_all_samples(self.variables, num_samples)
            df = pd.DataFrame(all_samples, columns=[var['name'] for var in self.variables])
            
            progress.update(task1, advance=1, info="Complete")
            
            # Second task: Evaluate objective
            task2 = progress.add_task(
                "[white]Evaluating objective function",
                total=len(df),
                info="Processing..."
            )
            
            # Evaluate objective function
            results = []
            for i, row in enumerate(df.values):
                y = self.objective_function(row.reshape(1, -1)).item()
                results.append(y)
                
                progress.update(
                    task2,
                    advance=1,
                    info=f"Sample {i+1}/{len(df)}"
                )
            
            df['y'] = results
            
        return df

    def print_summary(self, df: pd.DataFrame) -> None:
        """Print summary statistics in a nicely formatted table."""
        if not self.show_result:
            return
            
        console = Console()
        
        # Create statistics table
        table = Table(title="Summary Statistics", show_header=True, header_style="bold")
        table.add_column("Statistic")
        for col in df.columns:
            table.add_column(col)
            
        # Add rows
        stats = df.describe()
        for stat in stats.index:
            row = [stat]
            for col in stats.columns:
                val = stats.loc[stat, col]
                if isinstance(val, (int, float)):
                    row.append(f"{val:.6f}")
                else:
                    row.append(str(val))
            table.add_row(*row)
        
        console.print("\n")
        console.print(table)
        console.print("\n")

    def run(self, num_samples: int) -> None:
        """
        Run the initial design process and save results.
        
        Args:
            num_samples: Number of samples to generate
            
        Generated files:
            - training_data.csv: Contains generated samples and objective values
            - data_info.json: Contains metadata about variables and bounds
        """
        console = Console()
        
        # Generate samples
        df_simulation = self.generate_samples(num_samples)
        
        # Calculate input bounds
        input_bound = AdaptiveDistributionSampler.calculate_input_bounds(self.variables)
        
        # Save files
        simulation_file = os.path.join(self.output_dir, 'training_data.csv')
        df_simulation.to_csv(simulation_file, index=False)
        
        data_info = {
            'variables': self.variables,
            'variable_names': [var['name'] for var in self.variables],
            'input_bound': input_bound,
            'num_samples': len(df_simulation),
            'total_variables': len(self.variables)
        }
        
        info_file = os.path.join(self.output_dir, 'data_info.json')
        with open(info_file, 'w') as f:
            json.dump(data_info, f, indent=4)
        
        # Show results if enabled
        if self.show_result:
            # Print summary statistics
            self.print_summary(df_simulation)
            
            # Print completion message
            console.print("\n[green]✓ Initial design completed successfully![/green]")
            console.print(f"[white]• Samples saved: {simulation_file}[/white]")
            console.print(f"[white]• Metadata saved: {info_file}[/white]\n")

# Example usage
if __name__ == "__main__":
    # Define objective function (example from the original code)
    def true_function(x):
        X1, X2 = x[:, 0], x[:, 1]
        a1, x1, y1, sigma_x1, sigma_y1 = 100, 3, 2.1, 3, 3
        a2, x2, y2, sigma_x2, sigma_y2 = 150, -1.5, -1.2, 1, 1
        f = -(
            a1 * np.exp(-((X1 - x1) ** 2 / (2 * sigma_x1 ** 2) + (X2 - y1) ** 2 / (2 * sigma_y1 ** 2))) +
            a2 * np.exp(-((X1 - x2) ** 2 / (2 * sigma_x2 ** 2) + (X2 - y2) ** 2 / (2 * sigma_y2 ** 2))) - 200
        )
        return f
    

    # Create initial design instance
    design = InitialDesign(
    objective_function=true_function,
)
    
    # Add design variables
    design.add_design_variable(
        name='x1',
        range_bounds=[-5, 5],
        cov=0.1,
        description='first design variable'
    )
    
    design.add_design_variable(
        name='x2',
        range_bounds=[-6, 6],
        cov=0.1,
        description='second design variable'
    )
    
    
    # Run initial design
    design.run(num_samples=50)

    


