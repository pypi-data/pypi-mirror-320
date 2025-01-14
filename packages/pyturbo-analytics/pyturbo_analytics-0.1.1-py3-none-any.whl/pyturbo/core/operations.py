"""Core operations for PyTurbo."""

import concurrent.futures
import numpy as np
import pandas as pd
import dask.dataframe as dd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, Any, Union, Optional
from ..config import get_config
import multiprocessing

def chunk_dataframe(df, num_chunks):
    """Split dataframe into chunks for parallel processing."""
    chunk_size = len(df) // num_chunks
    return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

def rolling_window_numpy(arr, window, min_periods=None):
    """Fast rolling window calculations using numpy."""
    if min_periods is None:
        min_periods = window
    
    n = len(arr)
    result = np.full(n, np.nan)
    
    # Use numpy's stride tricks for efficient rolling window
    if n >= window:
        # Create rolling window view
        shape = (n - window + 1, window)
        strides = (arr.strides[0], arr.strides[0])
        windows = np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)
        
        # Calculate percentiles for each window
        result[window-1:] = np.percentile(windows, 75, axis=1)
    
    # Handle partial windows at the start
    for i in range(min(n, window-1)):
        if i + 1 >= min_periods:
            result[i] = np.percentile(arr[0:i+1], 75)
    
    return result

def optimized_rolling(series: pd.Series, window: int, min_periods: Optional[int] = None) -> pd.Series:
    """Optimized rolling window calculations."""
    # Convert to numpy array for faster processing
    values = series.to_numpy()
    
    # Process in chunks for better memory efficiency
    chunk_size = 100000
    if len(values) > chunk_size:
        chunks = [values[i:i + chunk_size] for i in range(0, len(values), chunk_size)]
        results = []
        
        for i, chunk in enumerate(chunks):
            # Add overlap to ensure correct rolling calculations
            if i > 0:
                chunk = np.concatenate([chunks[i-1][-window+1:], chunk])
            
            result = rolling_window_numpy(chunk, window, min_periods)
            
            # Remove overlap from result
            if i > 0:
                result = result[window-1:]
            
            results.append(result)
        
        result = np.concatenate(results)
    else:
        result = rolling_window_numpy(values, window, min_periods)
    
    return pd.Series(result, index=series.index)

def parallel_rolling(df: pd.Series, window: int, min_periods: Optional[int] = None, 
                    num_workers: Optional[int] = None) -> pd.Series:
    """Parallel rolling window calculations."""
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()
    
    # Split series into chunks with overlap
    chunk_size = len(df) // num_workers
    chunks = []
    for i in range(num_workers):
        start = i * chunk_size
        end = start + chunk_size if i < num_workers - 1 else len(df)
        
        # Add overlap for correct rolling calculations
        if i > 0:
            start = max(0, start - window + 1)
        chunk = df[start:end]
        chunks.append((chunk, i > 0))
    
    def process_chunk(args):
        chunk, has_overlap = args
        result = optimized_rolling(chunk, window, min_periods)
        if has_overlap:
            result = result[window-1:]
        return result
    
    # Process each chunk in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_chunk, chunks))
    
    # Combine results
    return pd.concat(results)

def parallel_apply(df: Union[pd.DataFrame, 'TurboFrame'], func: Callable, 
                  num_workers: int = None) -> pd.Series:
    """Apply a function to each row of the dataframe in parallel."""
    if hasattr(df, 'data'):
        df = df.data
    
    # Determine optimal number of workers
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()
    
    # For very small dataframes, don't parallelize
    if len(df) < 1000:
        return pd.Series(df.apply(func, axis=1), index=df.index)
    
    # Split dataframe into chunks
    chunks = chunk_dataframe(df, num_workers)
    
    def process_chunk(chunk):
        # Convert chunk to numpy arrays for faster computation
        chunk_dict = {col: chunk[col].to_numpy() for col in chunk.columns}
        results = []
        for i in range(len(chunk)):
            row = {k: v[i] for k, v in chunk_dict.items()}
            results.append(func(row))
        return results
    
    # Use ProcessPoolExecutor for CPU-bound operations
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        chunk_results = list(executor.map(process_chunk, chunks))
    
    # Combine results
    results = []
    for chunk in chunk_results:
        results.extend(chunk)
    
    return pd.Series(results, index=df.index)

def vectorized_apply(df: Union[pd.DataFrame, 'TurboFrame'], func: Callable) -> pd.Series:
    """Apply a vectorized function to the dataframe."""
    if hasattr(df, 'data'):
        df = df.data
    return func(df)

def gpu_accelerate(df: Union[pd.DataFrame, 'TurboFrame']) -> 'TurboFrame':
    """Convert a DataFrame to use GPU acceleration using RAPIDS cuDF."""
    try:
        import cudf
        from .frame import TurboFrame
        if hasattr(df, 'data'):
            df = df.data
        gpu_df = cudf.DataFrame.from_pandas(df)
        return TurboFrame(gpu_df, use_gpu=True)
    except ImportError:
        raise ImportError(
            "GPU acceleration requires RAPIDS cuDF. "
            "Install it with: pip install cudf-cuda11x"
        )

def optimize_numeric(df: Union[pd.DataFrame, 'TurboFrame']) -> 'TurboFrame':
    """Optimize memory usage for numeric columns."""
    from .frame import TurboFrame
    if hasattr(df, 'data'):
        df = df.data
        
    # Optimize integers
    int_cols = df.select_dtypes(include=['int']).columns
    for col in int_cols:
        col_min = df[col].min()
        col_max = df[col].max()
        
        # Select the smallest possible integer dtype
        if col_min >= 0:
            if col_max < 2**8:
                df[col] = df[col].astype(np.uint8)
            elif col_max < 2**16:
                df[col] = df[col].astype(np.uint16)
            elif col_max < 2**32:
                df[col] = df[col].astype(np.uint32)
        else:
            if col_min > -2**7 and col_max < 2**7:
                df[col] = df[col].astype(np.int8)
            elif col_min > -2**15 and col_max < 2**15:
                df[col] = df[col].astype(np.int16)
            elif col_min > -2**31 and col_max < 2**31:
                df[col] = df[col].astype(np.int32)
    
    # Optimize floats
    float_cols = df.select_dtypes(include=['float']).columns
    for col in float_cols:
        # Check if float32 precision is sufficient
        float32_series = df[col].astype(np.float32)
        if (df[col] - float32_series).abs().max() < 1e-6:
            df[col] = float32_series
    
    return TurboFrame(df)

class ComputeEngine:
    """Handles computation strategies and optimizations."""
    
    def __init__(self, num_threads=None):
        """Initialize compute engine with specified number of threads."""
        self._config = get_config()
        self._num_threads = num_threads or self._config.get('num_threads', None)
        self._thread_pool = ThreadPoolExecutor(max_workers=self._num_threads)
    
    def process_chunk(self, chunk, func):
        """Process a single chunk of data."""
        return func(chunk)
    
    def parallel_process(self, data, func, chunks=None):
        """Process data in parallel using multiple threads."""
        if isinstance(data, pd.DataFrame):
            if chunks is None:
                chunks = len(data) // (self._num_threads * 4)
            ddf = dd.from_pandas(data, npartitions=chunks)
            return ddf.map_partitions(func).compute(scheduler='threads')
        return func(data)
    
    def optimize(self, data):
        """Apply various optimizations to the data."""
        if isinstance(data, pd.DataFrame):
            # Convert to appropriate dtypes
            for col in data.select_dtypes(include=['int64']).columns:
                data[col] = pd.to_numeric(data[col], downcast='integer')
            for col in data.select_dtypes(include=['float64']).columns:
                data[col] = pd.to_numeric(data[col], downcast='float')
        return data
    
    def compute(self, data, optimize=True):
        """Compute final results, optionally applying optimizations."""
        if optimize:
            data = self.optimize(data)
        if isinstance(data, dd.DataFrame):
            return data.compute(scheduler='processes')
        return data
    
    def __del__(self):
        """Cleanup resources."""
        self._thread_pool.shutdown(wait=False)

# Create a global compute engine instance
compute_engine = ComputeEngine()
