import pickle
import os
from neuronica.utils.backend import backend
from neuronica.layers.layer import Layer, Dense, Convolutional, Reshape
import numpy as np

def save_model(model, filepath):
    """
    Save a model's architecture and weights to disk.
    
    Args:
        model: The Model instance to save
        filepath: Path where the model should be saved
    """
    # Create a dictionary to store model data
    model_data = {
        'layer_types': [],
        'layer_configs': [],
        'weights': []
    }
    
    # Store each layer's configuration and weights
    for layer in model.layers:
        # Store layer type
        model_data['layer_types'].append(layer.__class__.__name__)
        
        # Store layer configuration
        if hasattr(layer, 'get_config'):
            config = layer.get_config()
        else:
            config = {}
            
        if hasattr(layer, 'weights'):
            config['weights'] = backend.to_numpy(layer.weights)
        if hasattr(layer, 'bias'):
            config['bias'] = backend.to_numpy(layer.bias)
        if hasattr(layer, 'kernels'):
            config['kernels'] = backend.to_numpy(layer.kernels)
        if hasattr(layer, 'biases'):
            config['biases'] = backend.to_numpy(layer.biases)
            
        model_data['layer_configs'].append(config)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save to disk
    with open(filepath, 'wb') as f:
        pickle.dump(model_data, f)
        print(f"Model saved to {filepath}")

def load_model(filepath):
    """
    Load a model from disk.
    
    Args:
        filepath: Path to the saved model file
        
    Returns:
        A Model instance with the loaded architecture and weights
    """
    from neuronica import Model
    from neuronica.layers import Dense, Convolutional, Reshape
    from neuronica.layers.activations import Sigmoid, Tanh
    
    # Load model data
    with open(filepath, 'rb') as f:
        model_data = pickle.load(f)
    
    # Create layer mapping
    layer_classes = {
        'Dense': Dense,
        'Convolutional': Convolutional,
        'Reshape': Reshape,
        'Sigmoid': Sigmoid,
        'Tanh': Tanh
    }
    
    # Reconstruct layers
    layers = []
    for layer_type, config in zip(model_data['layer_types'], model_data['layer_configs']):
        # Get layer class
        LayerClass = layer_classes[layer_type]
        
        # Create layer
        if layer_type == 'Dense':
            layer = LayerClass(config['input_size'], config['output_size'])
            if 'weights' in config:
                layer.weights = backend.from_numpy(config['weights'])
            if 'bias' in config:
                layer.bias = backend.from_numpy(config['bias'])
                
        elif layer_type == 'Convolutional':
            layer = LayerClass(config['input_shape'], config['kernel_size'], config['depth'])
            if 'kernels' in config:
                layer.kernels = backend.from_numpy(config['kernels'])
            if 'biases' in config:
                layer.biases = backend.from_numpy(config['biases'])
                
        elif layer_type == 'Reshape':
            layer = LayerClass(config['input_shape'], config['output_shape'])
            
        elif layer_type in ['Sigmoid', 'Tanh']:
            layer = LayerClass()
            
        layers.append(layer)
    
    print(f"Model loaded from {filepath}")
    # Create and return model
    return Model(layers)

# Add get_config method to necessary layer classes
def add_config_methods():
    def dense_config(self):
        return {
            'input_size': self.weights.shape[1],
            'output_size': self.weights.shape[0]
        }
    
    def conv_config(self):
        return {
            'input_shape': self.input_shape,
            'kernel_size': self.kernels.shape[2],
            'depth': self.depth
        }
    
    def reshape_config(self):
        return {
            'input_shape': self.input_shape,
            'output_shape': self.output_shape
        }
        
    Dense.get_config = dense_config
    Convolutional.get_config = conv_config
    Reshape.get_config = reshape_config