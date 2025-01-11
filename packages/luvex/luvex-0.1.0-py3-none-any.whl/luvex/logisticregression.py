import numpy as np
from sklearn.base import BaseEstimator

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class Logisticregression(BaseEstimator):
    def __init__(self, learn_rate=0.01, n_iter=1000):
        self.learn_rate = learn_rate
        self.n_iter = n_iter
        self.Weights = None
        self.Bias = None

    def fit(self, X, y):  
        self.l, self.b = X.shape
        self.Weights = np.zeros(self.b)
        self.Bias = 0
        self.X = X
        self.y = y
        self.gradient_descent()
        for i in range(self.n_iter):
            self.gradient_descent()
        return self

    def gradient_descent(self):
        z = np.dot(self.X, self.Weights) + self.Bias
        sigm = sigmoid(z)
        y_hat = sigm - self.y.T
        y_hat = np.reshape(y_hat, self.l)
        diff_W = np.dot(self.X.T, y_hat) / self.l
        diff_b = np.sum(y_hat) / self.l

        self.Weights = self.Weights - (self.learn_rate * diff_W)
        self.Bias = self.Bias - (self.learn_rate * diff_b)

    def predict(self, X):
        z = np.dot(X, self.Weights) + self.Bias
        z_final = sigmoid(z)
        y_predict = np.where(z_final > 0.5, 1, 0)
        return y_predict

    def accu_score(self, X, y):
        acc_score = []
        self.fit(X, y)  # Fit the model
    
        for epoch in range(10):  
            y_pred = self.predict(X)  # Get predictions
            acc = np.mean(y_pred == y)  # Calculate accuracy
            print(f"Epoch {epoch + 1}: Accuracy = {acc:.2f}")
            acc_score.append(acc)
    
        print("Training has been completed.")
        return acc_score

    def get_params(self, deep=True):
        return {"learn_rate": self.learn_rate, "n_iter": self.n_iter}

    def set_params(self, **params):
        for param, value in params.items():
            setattr(self, param, value)
        return self
