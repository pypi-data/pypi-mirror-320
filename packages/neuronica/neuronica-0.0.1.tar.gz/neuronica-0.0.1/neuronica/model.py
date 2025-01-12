from neuronica.utils.backend import backend
import time
from datetime import timedelta

class Model:
    def __init__(self, layers: list):
        self.layers = layers

    def predict(self, input):
        """Perform a forward pass through all layers."""
        output = input
        for layer in self.layers:
            output = layer.forward(output)
        return output

    def train(self, loss, loss_prime, x_train, y_train, epochs=1000, learning_rate=0.001, batch_size=32, verbose=True):
        """
        Train the model using the provided loss function and training data.
        
        Args:
            loss: Loss function to calculate error.
            loss_prime: Derivative of the loss function for backpropagation.
            x_train: Training inputs (NumPy or CuPy arrays).
            y_train: Training targets (NumPy or CuPy arrays).
            epochs: Number of training epochs.
            learning_rate: Learning rate for gradient descent.
            batch_size: Size of mini-batches for training.
            verbose: Whether to print progress at each epoch.
        """
        x_train = backend.from_numpy(x_train)
        y_train = backend.from_numpy(y_train)
        n_samples = len(x_train)
        
        start_time = time.time()

        for e in range(epochs):
            error = 0
            # Create batches
            indices = backend.xp.random.permutation(n_samples)
            for i in range(0, n_samples, batch_size):
                batch_idx = indices[i:min(i + batch_size, n_samples)]
                x_batch = x_train[batch_idx]
                y_batch = y_train[batch_idx]
                
                for x, y in zip(x_batch, y_batch):
                    output = self.predict(x)
                    error += loss(y, output)
                    grad = loss_prime(y, output)
                    for layer in reversed(self.layers):
                        grad = layer.backward(grad, learning_rate)
                        
            error /= n_samples
            # Improved progress display
            if verbose:
                print(f"Epoch {e + 1}/{epochs}\t| Error: {backend.to_numpy(error):.6f}")
            elif e % (epochs // 10) == 0:
                print(f"Epoch {e + 1}/{epochs}\t| Error: {backend.to_numpy(error):.6f}")
        
        elapsed_time = time.time() - start_time  # Calculate time taken
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        print(f"\nTraining completed in {int(hours)}h {int(minutes)}m {int(seconds)}s.")
    
    def save(self, filepath):
        """Save model architecture and weights to disk."""
        from neuronica.utils.serialization import save_model
        save_model(self, filepath)

    @classmethod
    def load(cls, filepath):
        """Load model from disk."""
        from neuronica.utils.serialization import load_model
        return load_model(filepath)