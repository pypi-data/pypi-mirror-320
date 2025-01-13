import numpy as np
from sklearn.base import BaseEstimator

class Linearregression(BaseEstimator):
    def __init__(self, learning_rate=0.01, epochs=1000):
        """
        Linear Regression model implemented from scratch.
        Includes gradient descent optimization with a bias term.
        """
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights = None
        self.mean_X = None
        self.std_X = None

    def fit(self, X, y):
        """
        Fit the linear regression model using gradient descent.
        """
        m, n = X.shape

        # Normalize the input data (X)
        self.mean_X = np.mean(X, axis=0)
        self.std_X = np.std(X, axis=0)
        X_normalized = (X - self.mean_X) / self.std_X

        # Add bias term (intercept) to the features
        X_normalized = np.c_[np.ones(X_normalized.shape[0]), X_normalized]

        # Initialize weights (including bias)
        self.weights = np.zeros(X_normalized.shape[1])

        # Gradient Descent
        for epoch in range(self.epochs):
            # Predictions
            y_pred = X_normalized.dot(self.weights)

            # Compute Gradients
            errors = y_pred - y
            gradients = (2 / m) * X_normalized.T.dot(errors)

            # Update Weights
            self.weights -= self.learning_rate * gradients

            # Optional: Track Cost
            if epoch % (self.epochs // 10) == 0 or epoch == self.epochs - 1:
                cost = np.mean(errors ** 2)
                print(f"Epoch {epoch}: Cost={cost:.4f}")

        return self

    def predict(self, X_test):
        """
        Predict the labels for the test data.
        """
        # Normalize the test data using the mean and std from the training data
        X_test_normalized = (X_test - self.mean_X) / self.std_X

        # Add bias term (intercept) to the features
        X_test_normalized = np.c_[np.ones(X_test_normalized.shape[0]), X_test_normalized]

        # Predictions
        return X_test_normalized.dot(self.weights).flatten()

    def accuracy_metric_RMSE(self, X_test, y_test):
        """
        Calculate the RMSE (Root Mean Squared Error) metric for the model.
        """
        y_pred = self.predict(X_test)
        mse = np.mean((y_test - y_pred) ** 2)
        rmse = np.sqrt(mse)
        return rmse

    def get_params(self, deep=True):
        """
        Return the hyperparameters of the model.
        """
        return {"learning_rate": self.learning_rate, "epochs": self.epochs}

    def set_params(self, **params):
        """
        Set hyperparameters for the model.
        """
        for param, value in params.items():
            setattr(self, param, value)
        return self
