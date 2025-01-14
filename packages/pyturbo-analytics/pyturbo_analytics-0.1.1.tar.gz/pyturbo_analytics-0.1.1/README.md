# PyTurbo: High-Performance Data Analysis Library

PyTurbo is a high-performance Python library designed for accelerated data analysis, leveraging both CPU and GPU computing paradigms. It provides significant speedups over traditional pandas operations through vectorized operations and parallel processing.

## 🚀 Key Features

- **High Performance**: Up to 120x speedup for complex calculations
- **GPU Acceleration**: Seamless integration with RAPIDS cuDF for GPU-powered computing
- **Automatic Optimization**: Smart fallback to CPU when GPU is unavailable
- **Pandas Compatible**: Familiar pandas-like API for easy adoption
- **Memory Efficient**: Optimized memory usage for large datasets

## 📊 Benchmark Results

| Operation | PyTurbo | Pandas | Speedup |
|-----------|---------|--------|---------|
| Complex Scoring | 0.16s | 19.15s | 120x |
| Rolling Ops | 3.49s | 36.15s | 10x |
| Filtering | 0.06s | 0.11s | 1.7x |

## 🛠 Installation

### Basic Installation (CPU Only)
```bash
pip install pyturbo
```

### GPU-Accelerated Installation
For GPU support, you'll need NVIDIA CUDA toolkit and RAPIDS cuDF:

1. Install CUDA Toolkit (11.x recommended):
   ```bash
   # Visit https://developer.nvidia.com/cuda-downloads
   ```

2. Install RAPIDS cuDF:
   ```bash
   pip install cudf-cuda11x
   ```

3. Install PyTurbo with GPU support:
   ```bash
   pip install pyturbo[gpu]
   ```

## 🎯 Quick Start

```python
import pyturbo as pt
import pandas as pd

# Create a TurboFrame from pandas DataFrame
df = pd.read_csv('large_dataset.csv')
tf = pt.TurboFrame(df)

# Automatic GPU acceleration if available
tf = tf.gpu()  # Falls back to CPU if GPU unavailable

# Complex calculations up to 120x faster
scores = tf['value'].apply(complex_calculation)

# Optimized rolling operations (10x faster)
rolling_stats = tf['value'].rolling(window=1000).apply(lambda x: np.percentile(x, 75))
```

## 🔍 Example: Vehicle Analysis

```python
import pyturbo as pt
import numpy as np

# Load data
df = pd.read_csv('vehicle_data.csv')
tf = pt.TurboFrame(df)

# Complex vehicle scoring (120x faster than pandas)
scores = pt.complex_vehicle_score_vectorized(tf)

# Efficient rolling calculations (10x faster)
rolling_scores = tf['score'].rolling(1000).apply(
    lambda x: np.percentile(x, 75), 
    engine='numpy'
)

# Group analysis with automatic optimization
stats = tf.groupby('category').agg({
    'speed': ['mean', 'std'],
    'score': ['mean', 'max']
})
```

## 🌟 Advanced Features

### GPU Acceleration
```python
# Check GPU availability
tf = pt.TurboFrame(df)
print(f"GPU Available: {tf.gpu_available}")

# Enable GPU processing
tf = tf.gpu()  # Automatic fallback to CPU if needed
```

### Parallel Processing
```python
# Automatic parallel processing for CPU operations
result = tf.parallel_apply(complex_function, num_workers=4)
```

### Memory Optimization
```python
# Efficient chunked processing for large datasets
chunks = tf.chunk_dataframe(num_chunks=4)
results = [chunk.process() for chunk in chunks]
```

## 📚 Documentation

For detailed documentation, visit [PyTurbo Documentation](https://pyturbo.readthedocs.io/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📝 License

PyTurbo is released under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Special thanks to the RAPIDS team for their amazing GPU-accelerated data science tools.
