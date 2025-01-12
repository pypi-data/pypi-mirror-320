from neuronica.utils.backend import backend

def mse(y_true, y_pred):
    """
    Mean Squared Error loss function.
    """
    return backend.xp.mean(backend.xp.power(y_true - y_pred, 2))

def mse_prime(y_true, y_pred):
    """
    Derivative of Mean Squared Error with respect to predictions.
    """
    return 2 * (y_pred - y_true) / backend.xp.size(y_true)

def binary_cross_entropy(y_true, y_pred):
    """
    Binary Cross-Entropy loss function.
    """
    epsilon = 1e-15
    y_pred = backend.xp.clip(y_pred, epsilon, 1 - epsilon)  # Ensure numerical stability
    return -backend.xp.mean(y_true * backend.xp.log(y_pred) + (1 - y_true) * backend.xp.log(1 - y_pred))

def binary_cross_entropy_prime(y_true, y_pred):
    """
    Derivative of Binary Cross-Entropy with respect to predictions.
    """
    epsilon = 1e-15
    y_pred = backend.xp.clip(y_pred, epsilon, 1 - epsilon)  # Ensure numerical stability
    return ((1 - y_true) / (1 - y_pred) - y_true / y_pred) / backend.xp.size(y_true)
