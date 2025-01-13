import numpy as np
from sklearn.base import BaseEstimator

class MultipleLinear(BaseEstimator):
    def __init__(self, learning_rate, iterations):
        self.learning_rate = learning_rate
        self.iterations = iterations

    def fit(self, X, y):
        self.X = X
        self.y = y.reshape(-1, 1)  # Ensure y is a column vector
        m = self.y.shape[0]
        self.theta = np.zeros((self.X.shape[1], 1))  # Initialize theta

        # Gradient descent
        for i in range(self.iterations):
            y_pred = np.dot(self.X, self.theta)  # Predictions
            d_theta = (1 / m) * np.dot(self.X.T, (y_pred - self.y))  # Gradient
            self.theta -= self.learning_rate * d_theta  # Update theta

        return self

    def predict(self, X):
        predictions = np.dot(X, self.theta)
        return predictions  # Return predictions as a 2D array

    def score(self, X, y):
        y_pred = self.predict(X)
        mse = np.mean(np.square(y_pred - y.reshape(-1, 1)))  # Mean Squared Error
        return mse

    def get_params(self, deep=True):
        return {"learning_rate": self.learning_rate, "iterations": self.iterations}

    def set_params(self, **params):
        for param, value in params.items():
            setattr(self, param, value)
        return self
