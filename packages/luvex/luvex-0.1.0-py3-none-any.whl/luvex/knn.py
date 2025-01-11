from collections import Counter
import numpy as np
from sklearn.base import BaseEstimator

class KNN(BaseEstimator):
    def __init__(self, k=3):
        self.k = k

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y.ravel()  # Flatten y to ensure it is a 1D array

    def predict(self, X):
        predictions = [self._predict(x) for x in X]
        return np.array(predictions)

    def _predict(self, x):
        distances = [self.euclidean_distance(x, x_train) for x_train in self.X_train]
        k_indices = np.argsort(distances)[:self.k]
        k_nearest_labels = [self.y_train[i] for i in k_indices]
        most_common = Counter(k_nearest_labels).most_common(1)
        return most_common[0][0]  # Return the most common label

    @staticmethod
    def euclidean_distance(x1, x2):
        # Compute the Euclidean distance between two points
        return np.sqrt(np.sum((x1 - x2) ** 2))

    def get_params(self, deep=True):
        # Return the hyperparameters as a dictionary
        return {'k': self.k}

    def set_params(self, **params):
        # Set the hyperparameters
        for param, value in params.items():
            setattr(self, param, value)
        return self
