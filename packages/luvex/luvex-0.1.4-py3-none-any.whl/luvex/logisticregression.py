import numpy as np
from sklearn.base import BaseEstimator

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class Logisticregression(BaseEstimator):
    def __init__(self, learn_rate=0.01, n_iter=1000, verbose=False):
        """
        Logistic Regression model with gradient descent.

        Parameters:
        - learn_rate: Learning rate for gradient updates.
        - n_iter: Number of iterations for training.
        - verbose: Whether to display intermediate results during training.
        """
        self.learn_rate = learn_rate
        self.n_iter = n_iter
        self.verbose = verbose
        self.Weights = None
        self.Bias = None

    def fit(self, X, y):
        """
        Train the logistic regression model using gradient descent.

        Parameters:
        - X: Feature matrix of shape (m, n).
        - y: Target vector of shape (m,).
        """
        self.l, self.b = X.shape
        self.Weights = np.zeros(self.b)
        self.Bias = 0
        self.X = X
        self.y = y

        for i in range(self.n_iter):
            self.gradient_descent()
            if self.verbose and i % (self.n_iter // 10) == 0:
                loss = self.compute_loss()
                print(f"Iteration {i}: Loss = {loss:.4f}")

        print("Training completed.")

    def gradient_descent(self):
        z = np.dot(self.X, self.Weights) + self.Bias
        sigm = sigmoid(z)
        y_hat = sigm - self.y
        diff_W = np.dot(self.X.T, y_hat) / self.l
        diff_b = np.sum(y_hat) / self.l

        self.Weights -= self.learn_rate * diff_W
        self.Bias -= self.learn_rate * diff_b

    def compute_loss(self):
        z = np.dot(self.X, self.Weights) + self.Bias
        sigm = sigmoid(z)
        loss = -np.mean(self.y * np.log(sigm) + (1 - self.y) * np.log(1 - sigm))
        return loss

    def predict(self, X):
        """
        Predict binary labels for the input data.

        Parameters:
        - X: Feature matrix of shape (m, n).

        Returns:
        - y_predict: Predicted labels of shape (m,).
        """
        z = np.dot(X, self.Weights) + self.Bias
        z_final = sigmoid(z)
        y_predict = np.where(z_final > 0.5, 1, 0)
        return y_predict

    def accu_score(self, X, y):
        """
        Calculate accuracy of the model.

        Parameters:
        - X: Feature matrix.
        - y: True labels.

        Returns:
        - acc_score: Accuracy score as a float.
        """
        y_pred = self.predict(X)
        acc = np.mean(y_pred == y)
        print(f"Accuracy = {acc:.2f}")
        return acc

    def get_params(self, deep=True):
        return {"learn_rate": self.learn_rate, "n_iter": self.n_iter, "verbose": self.verbose}

    def set_params(self, **params):
        for param, value in params.items():
            setattr(self, param, value)
        return self
