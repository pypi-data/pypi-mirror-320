import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray, float64

class Perceptron:
    def __init__(self, neuron_id: int, theta_size: int, learning_rate: float = 0.01, n_iter: int = 1000):
        self.id = neuron_id
        self.theta_ = np.random.randn(theta_size, 1)
        self.bias_ = np.random.randn(1)
        self.learning_rate_: float = learning_rate 
        self.n_iter_: int = n_iter
        self.epsilon = 10e-15
        self.loss_: list = []

    def __repr__(self) -> str:
        return f"Perceptron(id={self.id})"

    def fit(self, features, target, refit: bool = False):
        if refit:
            self.theta_ = np.random.randn(features.shape[1], 1)
            self.bias_ = np.random.randn(1)
            self.loss_: list = []

        for i in range(self.n_iter_):
            _proba = self.predict_proba(features)

            if self.n_iter_ > 100:
                if i % (self.n_iter_ // 100) == 0:
                    self.loss_.append(self.log_loss(target, _proba))
            else:
                self.loss_.append(self.log_loss(target, _proba))

            _target_size = len(target)
            _dp_theta = 1 / _target_size * np.dot(features.T, _proba - target)
            _dp_bias = 1 / _target_size * np.sum(_proba - target)
            self.update(_dp_theta, _dp_bias)

    def predict_proba(self, feature: ndarray):
        return 1 / (1 + np.exp(-(feature.dot(self.theta_) + self.bias_)))

    def log_loss(self, target: ndarray, proba: ndarray):
        return 1 / len(target) * np.sum(-target * np.log(proba + self.epsilon) - (1 - target) * np.log(1 - proba + self.epsilon))

    def update(self, dp_theta: ndarray, dp_bias: float64):
        self.theta_ -= self.learning_rate_ * dp_theta
        self.bias_ -= self.learning_rate_ * dp_bias

    def predict(self, data: ndarray):
        return (self.predict_proba(data) >= 0.5)[0][0]

    def display_loss(self):
        plt.plot(self.loss_)
        plt.show()

    def score(self):
        pass