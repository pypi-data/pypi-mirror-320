import abc
import numpy as np

class Layer(abc.ABC):
    def __init__(self, input_size, output_size):
        self.input_size = None
        self.output_size = None
        self.input_data = None
        self.output_data = None
        self.weights = np.random.rand(input_size, output_size) - 0.5
        self.bias = np.random.rand(1, output_size) - 0.5

    # calcule la sortie Y d'une couche pour une entrée X donnée
    def forward_propagation(self, data):
        raise NotImplementedError

    # calcule dE/dX pour un dE/dY donné (et met à jour les paramètres le cas échéant)
    def backward_propagation(self, output_error, learning_rate):
        raise NotImplementedError

class FCLayer(Layer):
    # Couche entièrement connectée
    # input_size = nombre de neurones d'entrée
    # output_size = nombre de neurones de sortie
    def __init__(self, input_size, output_size):
        super().__init__(input_size, output_size)


    # returns output for a given input
    def forward_propagation(self, input_data):
        self.input_data = input_data
        self.output_data = np.dot(self.input_data, self.weights) + self.bias
        return self.output_data

    # computes dE/dW, dE/dB for a given output_error=dE/dY. Returns input_error=dE/dX.
    def backward_propagation(self, output_error, learning_rate):
        input_error = np.dot(output_error, self.weights.T)
        weights_error = np.dot(self.input_data.T, output_error)
        # dBias = output_error

        # update parameters
        self.weights -= learning_rate * weights_error
        self.bias -= learning_rate * output_error
        return input_error

# inherit from base class Layer
class ActivationLayer(Layer):
    def __init__(self, activation, activation_prime, input_size, output_size):
        super().__init__(input_size, output_size)
        self.activation = activation
        self.activation_prime = activation_prime

    # returns the activated input
    def forward_propagation(self, input_data):
        self.input_data = input_data
        self.output_data = self.activation(self.input_data)
        return self.output_data

    # Returns input_error=dE/dX for a given output_error=dE/dY.
    # learning_rate is not used because there is no "learnable" parameters.
    def backward_propagation(self, output_error, learning_rate):
        return self.activation_prime(self.input_data) * output_error