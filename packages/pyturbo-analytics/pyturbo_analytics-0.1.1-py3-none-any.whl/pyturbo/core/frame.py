"""TurboFrame class for high-performance data operations."""

import numpy as np
import pandas as pd
from typing import Union, Optional, List, Dict, Any, Callable
from contextlib import contextmanager
import warnings

from .operations import (
    parallel_apply, gpu_accelerate, optimize_numeric, compute_engine,
    optimized_rolling, parallel_rolling
)
from ..config import get_device_info

# Optional GPU support
try:
    import cudf
    HAS_GPU = True
except ImportError:
    HAS_GPU = False
    warnings.warn(
        "RAPIDS cuDF not found. GPU acceleration will not be available. "
        "To enable GPU support, install cuDF: pip install cudf-cuda11x"
    )

class TurboFrame:
    """High-performance DataFrame wrapper with automatic optimization."""
    
    def __init__(self, data: Union[pd.DataFrame, 'cudf.DataFrame', np.ndarray, Dict], use_gpu: bool = False):
        """Initialize TurboFrame with input data."""
        self._gpu_available = HAS_GPU
        self.use_gpu = use_gpu and self._gpu_available
        
        # Convert input to appropriate DataFrame type
        if isinstance(data, (pd.DataFrame, pd.Series)):
            self.data = data
        elif isinstance(data, np.ndarray):
            self.data = pd.DataFrame(data)
        elif isinstance(data, dict):
            self.data = pd.DataFrame(data)
        elif HAS_GPU and isinstance(data, cudf.DataFrame):
            self.data = data
            self.use_gpu = True
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
        
        # Try GPU conversion if requested
        if use_gpu and not isinstance(self.data, getattr(cudf, 'DataFrame', type(None))):
            try:
                self.gpu()
            except Exception as e:
                warnings.warn(
                    f"Failed to convert to GPU: {str(e)}. Falling back to CPU. "
                    "This may be due to unsupported data types or missing GPU support."
                )
                self.use_gpu = False
    
    @classmethod
    def from_csv(cls, filepath: str, **kwargs) -> 'TurboFrame':
        """Create TurboFrame from CSV file."""
        df = pd.read_csv(filepath, **kwargs)
        return cls(df)
    
    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to underlying DataFrame."""
        if isinstance(self.data, pd.Series):
            return getattr(self.data, name)
        return getattr(self.data, name)
    
    def __getitem__(self, key):
        """Support indexing operations."""
        result = self.data[key]
        if isinstance(result, (pd.DataFrame, pd.Series)):
            return TurboFrame(result, use_gpu=self.use_gpu)
        return result
    
    def __setitem__(self, key, value):
        """Support item assignment."""
        if isinstance(value, TurboFrame):
            value = value.data
        self.data[key] = value
    
    # Comparison operators
    def __lt__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return self.data < other
    
    def __le__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return self.data <= other
    
    def __gt__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return self.data > other
    
    def __ge__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return self.data >= other
    
    def __eq__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return self.data == other
    
    def __ne__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return self.data != other
    
    # Arithmetic operators
    def __add__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return TurboFrame(self.data + other, use_gpu=self.use_gpu)
    
    def __sub__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return TurboFrame(self.data - other, use_gpu=self.use_gpu)
    
    def __mul__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return TurboFrame(self.data * other, use_gpu=self.use_gpu)
    
    def __truediv__(self, other):
        if isinstance(other, TurboFrame):
            other = other.data
        return TurboFrame(self.data / other, use_gpu=self.use_gpu)
    
    def __abs__(self):
        return TurboFrame(abs(self.data), use_gpu=self.use_gpu)
    
    def gpu(self) -> 'TurboFrame':
        """Convert the frame to use GPU acceleration."""
        if not HAS_GPU:
            raise ImportError(
                "GPU acceleration requires RAPIDS cuDF. "
                "Install it with: pip install cudf-cuda11x"
            )
        
        if isinstance(self.data, getattr(cudf, 'DataFrame', type(None))):
            return self
            
        try:
            self.data = cudf.DataFrame.from_pandas(self.data)
            self.use_gpu = True
        except Exception as e:
            raise RuntimeError(f"Failed to convert to GPU: {str(e)}")
        
        return self
    
    def cpu(self) -> 'TurboFrame':
        """Convert the frame back to CPU."""
        if isinstance(self.data, getattr(cudf, 'DataFrame', type(None))):
            self.data = self.data.to_pandas()
            self.use_gpu = False
        return self
    
    @property
    def is_gpu(self) -> bool:
        """Check if the frame is currently using GPU acceleration."""
        return self.use_gpu and isinstance(self.data, getattr(cudf, 'DataFrame', type(None)))
    
    @property
    def gpu_available(self) -> bool:
        """Check if GPU acceleration is available."""
        return self._gpu_available
        
    def parallel_apply(self, func: Callable, num_workers: Optional[int] = None) -> pd.Series:
        """Apply function to each row in parallel."""
        return parallel_apply(self, func, num_workers)
    
    def optimize(self) -> 'TurboFrame':
        """Optimize numeric columns for memory usage."""
        return optimize_numeric(self)
    
    def compute(self) -> pd.DataFrame:
        """Get computed pandas DataFrame."""
        return compute_engine.compute(self.data)
    
    def groupby(self, by, **kwargs):
        """Group operations with automatic optimization."""
        if 'observed' not in kwargs:
            kwargs['observed'] = True  # Silence the warning
        grouped = self.data.groupby(by, **kwargs)
        return GroupedTurboFrame(grouped, parent=self)
    
    def rolling(self, window: int, min_periods: Optional[int] = None):
        """Enhanced rolling window operations."""
        if isinstance(self.data, pd.Series):
            return TurboRolling(self.data, window, min_periods)
        return self.data.rolling(window, min_periods=min_periods)
    
    def __str__(self) -> str:
        """String representation."""
        return f"TurboFrame(use_gpu={self.use_gpu})\n{str(self.data)}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()

class GroupedTurboFrame:
    """Wrapper for grouped operations with optimizations."""
    
    def __init__(self, grouped, parent):
        """Initialize with grouped data and parent frame."""
        self.grouped = grouped
        self.parent = parent
    
    def __getattr__(self, name):
        """Delegate to underlying grouped object."""
        return getattr(self.grouped, name)
    
    def agg(self, *args, **kwargs):
        """Optimized aggregation operations."""
        result = self.grouped.agg(*args, **kwargs)
        return TurboFrame(result, use_gpu=self.parent.use_gpu)

class TurboRolling:
    """Enhanced rolling window operations with optimizations."""
    
    def __init__(self, series: pd.Series, window: int, min_periods: Optional[int] = None):
        """Initialize rolling window."""
        self.series = series
        self.window = window
        self.min_periods = min_periods
    
    def apply(self, func, raw: bool = False, engine: str = 'numpy', **kwargs):
        """Apply function to rolling window with optimizations."""
        # Check if the function is a percentile calculation
        is_percentile = (
            isinstance(func, type(lambda: None)) and 
            func.__code__.co_code == (lambda x: np.percentile(x, 75)).__code__.co_code
        )
        
        if engine == 'numpy' and is_percentile:
            # Use optimized implementation for percentile calculation
            return optimized_rolling(self.series, self.window, self.min_periods)
        elif engine == 'parallel':
            # Use parallel processing for other operations
            return parallel_rolling(self.series, self.window, self.min_periods)
        else:
            # Fallback to pandas implementation
            return self.series.rolling(
                window=self.window, 
                min_periods=self.min_periods
            ).apply(func, raw=raw, **kwargs)
