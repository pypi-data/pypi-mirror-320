from scipy import signal
import numpy as np
import cupyx.scipy.signal as cusignal
from neuronica.utils.backend import  backend

# _____ BASE LAYER _____
class Layer:
    def __init__(self):
        self.input = None
        self.output = None

    def forward(self, input):
        pass

    def backward(self, output_grad, learning_rate):
        pass


# _____ DENSE LAYER _____
class Dense(Layer):
    def __init__(self, input_size, output_size):
        scale = backend.xp.sqrt(2.0 / input_size)  # He initialization
        self.weights = backend.xp.random.randn(output_size, input_size) * scale
        self.bias = backend.xp.zeros((output_size, 1))  # Initialize bias to zero

    def forward(self, input):
        self.input = input
        return backend.xp.dot(self.weights, self.input) + self.bias  # y = xw + b

    def backward(self, output_grad, learning_rate):
        weight_gradient = backend.xp.dot(output_grad, self.input.T)  # dL/dw = dL/dy * dy/dw
        self.weights -= learning_rate * weight_gradient  # w = w - lr * dL/dw
        self.bias -= learning_rate * output_grad  # b = b - lr * dL/db
        return backend.xp.dot(self.weights.T, output_grad)  # dL/dx = dL/dy * dy/dx


# _____ CONVOLUTIONAL LAYER _____
class Convolutional(Layer):
    def __init__(self, input_shape, kernel_size, depth):
        input_depth, input_height, input_width = input_shape
        self.depth = depth
        self.input_shape = input_shape
        self.input_depth = input_depth
        self.output_shape = (depth, input_height - kernel_size + 1, input_width - kernel_size + 1)
        self.kernels_shape = (depth, input_depth, kernel_size, kernel_size)
        # Specify dtype explicitly to avoid CuPy warning
        self.kernels = backend.xp.random.randn(*self.kernels_shape).astype(backend.xp.float32)
        self.biases = backend.xp.random.randn(*self.output_shape).astype(backend.xp.float32)

    def forward(self, input):
        # Convert input to backend format (CuPy if using CUDA)
        self.input = backend.from_numpy(input) if isinstance(input, np.ndarray) else input
        self.input = self.input.astype(backend.xp.float32)
        self.output = backend.xp.copy(self.biases)
        
        for i in range(self.depth):
            for j in range(self.input_depth):
                if backend.use_cuda:
                    # Ensure arrays are in the correct format and type
                    input_arr = backend.xp.ascontiguousarray(self.input[j])
                    kernel_arr = backend.xp.ascontiguousarray(self.kernels[i, j])
                    self.output[i] += cusignal.correlate2d(input_arr, kernel_arr, mode='valid')
                else:
                    # Convert to NumPy for CPU computation
                    input_np = backend.to_numpy(self.input[j])
                    kernel_np = backend.to_numpy(self.kernels[i, j])
                    result = signal.correlate2d(input_np, kernel_np, mode='valid')
                    self.output[i] += backend.from_numpy(result)
        return self.output

    def backward(self, output_grad, learning_rate):
        kernels_gradient = backend.xp.zeros(self.kernels_shape, dtype=backend.xp.float32)
        input_gradient = backend.xp.zeros(self.input_shape, dtype=backend.xp.float32)
        output_grad = backend.from_numpy(output_grad) if isinstance(output_grad, np.ndarray) else output_grad
        output_grad = output_grad.astype(backend.xp.float32)

        for i in range(self.depth):
            for j in range(self.input_depth):
                if backend.use_cuda:
                    input_arr = backend.xp.ascontiguousarray(self.input[j])
                    output_grad_arr = backend.xp.ascontiguousarray(output_grad[i])
                    kernel_arr = backend.xp.ascontiguousarray(self.kernels[i, j])
                    
                    kernels_gradient[i, j] = cusignal.correlate2d(input_arr, output_grad_arr, mode='valid')
                    input_gradient[j] += cusignal.convolve2d(output_grad_arr, kernel_arr, mode='full')
                else:
                    input_np = backend.to_numpy(self.input[j])
                    output_grad_np = backend.to_numpy(output_grad[i])
                    kernel_np = backend.to_numpy(self.kernels[i, j])
                    
                    kg = signal.correlate2d(input_np, output_grad_np, mode='valid')
                    ig = signal.convolve2d(output_grad_np, kernel_np, mode='full')
                    
                    kernels_gradient[i, j] = backend.from_numpy(kg)
                    input_gradient[j] += backend.from_numpy(ig)

        self.kernels -= learning_rate * kernels_gradient
        self.biases -= learning_rate * output_grad
        return input_gradient


# _____ RESHAPE LAYER _____
class Reshape(Layer):
    def __init__(self, input_shape, output_shape):
        self.input_shape = input_shape
        self.output_shape = output_shape

    def forward(self, input):
        return backend.xp.reshape(input, self.output_shape)

    def backward(self, output_grad, learning_rate):
        return backend.xp.reshape(output_grad, self.input_shape)


# Example usage
if __name__ == "__main__":
    backend.use_cuda = True  # Enable CUDA support
    layer = Dense(10, 5)
    input_data = backend.xp.random.randn(10, 1)
    output = layer.forward(input_data)
    print("Forward output:", output)
