import numpy as np
from sklearn.base import BaseEstimator

class Linearregression(BaseEstimator):
    def __init__(self, learning_rate=0.01, epochs=1000):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.a = 0  # Slope (weight)
        self.b = 0  # Intercept (bias)

    def fit(self, X, y):
        """
        Fit the linear regression model using gradient descent.
        """
        self.Data = X
        self.Label = y
        m = len(X)

        # Gradient Descent Loop
        for epoch in range(self.epochs):
            # Predictions
            y_pred = self.a * X + self.b

            # Compute Gradients
            da = (-2 / m) * np.sum((y - y_pred) * X)  # Gradient for a
            db = (-2 / m) * np.sum(y - y_pred)       # Gradient for b

            # Update Weights
            self.a -= self.learning_rate * da
            self.b -= self.learning_rate * db

            # Optional: Track Progress
            if epoch % (self.epochs // 10) == 0:
                cost = np.mean((y - y_pred) ** 2)  # Mean Squared Error
                print(f"Epoch {epoch}: Cost={cost:.4f}, a={self.a:.4f}, b={self.b:.4f}")

        return self

    def predict(self, X_test):
        """
        Predict the labels for the test data.
        """
        # Handle potential NaN issues in X_test
        if np.std(X_test) != 0:
            X_test = (X_test - np.mean(X_test)) / np.std(X_test)
        return self.a * X_test + self.b

    def accuracy_metric_RMSE(self, X_test, Y_test):
        """
        Calculate the RMSE (Root Mean Squared Error) metric for the model.
        """
        Y_pred = self.predict(X_test)
        mse = np.mean((Y_test - Y_pred) ** 2)
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
