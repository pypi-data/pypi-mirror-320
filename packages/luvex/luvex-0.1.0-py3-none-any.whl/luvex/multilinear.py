from sklearn.base import BaseEstimator
import numpy as np

class MultipleLinear(BaseEstimator):

    def __init__(self, learning_rate, iterations):
        self.learning_rate = learning_rate
        self.iterations = iterations

    def fit(self, X, y):
        self.X = X
        self.y = y
        m = self.y.size
        self.theta = np.zeros((self.X.shape[1], 1))  # Initialize theta

        # Gradient descent
        for i in range(self.iterations):
            y_pred = np.dot(self.X, self.theta)
            cost = (1 / (2 * m)) * np.sum(np.square(y_pred - self.y))

            d_theta = (1 / m) * np.dot(self.X.T, y_pred - self.y)
            self.theta -= self.learning_rate * d_theta  # Update theta

            if i % (self.iterations // 10) == 0:
                print("Cost is :", cost)

    def predict(self):
        # Calculate predictions using learned parameters (theta)
        y_pred = np.dot(self.X, self.theta)
        return y_pred.flatten()  # Return as 1D array

    def score(self):
        # Call the predict function and return the cost (or R^2 score, depending on the requirement)
        y_pred = self.predict()
        cost = np.mean(np.square(y_pred - self.y))  # Mean Squared Error (MSE)
        return cost

    def get_params(self, deep=True):
        # Return hyperparameters as a dictionary
        return {"learning_rate": self.learning_rate, "iterations": self.iterations}

    def set_params(self, **params):
        # Set hyperparameters
        for param, value in params.items():
            setattr(self, param, value)
        return self
