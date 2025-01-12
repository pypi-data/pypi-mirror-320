# _____ ACTIVATION LAYER _____
"""
    Applies an activation function to the input.
"""
from neuronica.layers.layer import Layer
from neuronica.utils.backend import backend

class Activation(Layer):
    def __init__(self, activation, activation_prime):
        self.activation = activation
        self.activation_prime = activation_prime

    def forward(self, input):
        # Save the input for the backward pass
        self.input = input
        return self.activation(self.input)
    
    def backward(self, output_grad, learning_rate):
        # return output_grad * self.activation_prime(self.input)
        return backend.xp.multiply(output_grad, self.activation_prime(self.input))

# _____ ACTIVATION FUNCTIONS _____

"""
    Tanh activation function.
    (exp(x) - exp(-x)) / (exp(x) + exp(-x))
"""
class Tanh(Activation):
    def __init__(self):
        tanh = lambda x: backend.xp.tanh(x)
        tanh_prime = lambda x: 1 - backend.xp.tanh(x)**2
        super().__init__(tanh, tanh_prime)


"""
    Sigmoid activation function.
    1 / (1 + exp(-x))
"""
class Sigmoid(Activation):
    def __init__(self):
        sigmoid = lambda x: 1 / (1 + backend.xp.exp(-backend.xp.clip(x, -500, 500)))
        sigmoid_prime = lambda x: sigmoid(x) * (1 - sigmoid(x))
        super().__init__(sigmoid, sigmoid_prime)


"""
    Softmax activation function.
    exp(x) / sum(exp(x))
"""
class Softmax(Layer):
    def forward(self, input):
        tmp = backend.xp.exp(input)
        self.output = tmp / backend.xp.sum(tmp)
        return self.output
    
    def backward(self, output_grad, learning_rate):
        n = backend.xp.size(self.output)
        return backend.xp.dot((backend.xp.identity(n) - self.output.T) * self.output, output_grad)