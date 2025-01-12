# backend.py
import numpy as np
import cupy as cp

class Backend:
    def __init__(self):
        self.use_cuda = False  # Default to CPU
        self.xp = np  # Start with NumPy

        self.warmup()  # Warm up the GPU
    
    def warmup(self):
        """Warm up the GPU by performing a simple operation."""
        self.xp.dot(self.xp.ones((10, 10)), self.xp.ones((10, 10)))

    def set_cuda(self, use_cuda: bool):
        """Set whether to use CUDA (CuPy) or CPU (NumPy)."""
        try:
            if use_cuda:
                import cupy as cp
                self.xp = cp
            else:
                self.xp = np
            self.use_cuda = use_cuda
        except ImportError:
            print("CuPy not installed. Defaulting to CPU (NumPy).")
            self.use_cuda = False
            self.xp = np

    def to_numpy(self, array):
        """Convert CuPy array to NumPy array if using CuPy; otherwise, return unchanged."""
        if self.use_cuda:
            return cp.asnumpy(array)
        return array

    def from_numpy(self, array):
        """Convert NumPy array to CuPy array if using CuPy; otherwise, return unchanged."""
        if self.use_cuda:
            return cp.array(array)
        return array

# Create a singleton instance for global use
backend = Backend()
