import numpy as np
from mymodels.utils import accuracy_score


class LogisticRegression:
    def __init__(self, lr=0.01, n_iters=1000):
        self.lr = lr
        self.n_iters = n_iters
        self.weights = None

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):  # Ensure this line is properly indented
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0  # Initialize the bias term
        
        for _ in range(self.n_iters):
            # Calculate the linear model
            linear_model = np.dot(X, self.weights) + self.bias  # Add bias term
            predictions = self.sigmoid(linear_model)
            
            # Compute the gradient with respect to weights and bias
            gradient_weights = np.dot(X.T, (predictions - y)) / n_samples
            gradient_bias = np.sum(predictions - y) / n_samples
            
            # Update the weights and bias
            self.weights -= self.lr * gradient_weights
            self.bias -= self.lr * gradient_bias

    def predict(self, X):
        linear_model = np.dot(X, self.weights)
        return self.sigmoid(linear_model) >= 0.5

    def score(self, X, y):
        predictions = self.predict(X).astype(int)
        return accuracy_score(y, predictions)
