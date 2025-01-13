import numpy as np
from mymodels.utils import accuracy_score

class LinearRegression:
    def __init__(self):
        self.weights = None

    def fit(self, X, y):
        X = np.insert(X, 0, 1, axis=1)  # Add intercept
        self.weights = np.linalg.pinv(X.T @ X) @ X.T @ y

    def predict(self, X):
        X = np.insert(X, 0, 1, axis=1)
        return X @ self.weights

    def score(self, X, y):
        predictions = self.predict(X)
        return accuracy_score(y, predictions.round())  # For classification-like tasks
