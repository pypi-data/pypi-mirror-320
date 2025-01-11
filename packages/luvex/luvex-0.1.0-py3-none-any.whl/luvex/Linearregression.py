from sklearn.base import BaseEstimator
from sklearn.utils import shuffle
from numpy import random
import numpy as np

def mean(x):
    return sum(x)/len(x)

class Linearregression(BaseEstimator):
    
    def __init__(self):
        self.Data = []
        self.Label = []
        self.length_data = 0

    def fit(self, X, y):
        """
        Fit the linear regression model to the data.
        """
        self.Data = X
        self.Label = y
        self.length_data = len(X)
        return self  # Return self to allow chaining of methods

    def coeff_cal(self):
        """
        Calculate the coefficients (a, b) for the linear regression model.
        """
        a_cal = 0
        b_cal = 0
        self.Data, self.Label = shuffle(self.Data, self.Label, random_state=random.randint(1, 10000))

        for i in range(self.length_data):
            a_cal += (self.Data[i] - mean(self.Data)) * (self.Label[i] - mean(self.Label))
            b_cal += (self.Data[i] - mean(self.Data))**2

        a_final = a_cal / b_cal
        b_final = mean(self.Label) - (a_final * mean(self.Data))
        return a_final, b_final

    def predict(self, X_test):
        """
        Predict the labels for the test data.
        """
        a, b = self.coeff_cal()
        Y_pred_label = []
        for val in X_test:
            y_pred = (a * val) + b
            Y_pred_label.append(y_pred)
        return np.array(Y_pred_label)

    def predict_single(self, X):
        """
        Predict a single value using the learned coefficients.
        """
        a, b = self.coeff_cal()
        y_pred = (a * X) + b
        return y_pred

    def accuracy_metric_RMSE(self, X_test, Y_test, epochs):
        """
        Calculate the RMSE (Root Mean Squared Error) metric for the model.
        """
        acc_score = []
        for epoch in range(epochs):
            Y_pred = self.predict(X_test)
            rsme = 0
            for i in range(len(Y_test)):
                rsme += (Y_test[i] - Y_pred[i])**2
            arr = np.sqrt(rsme / len(Y_test)) / 10000
            acc_score.append(arr)
        return acc_score

    def get_params(self, deep=True):
        """
        Return the parameters of the model.
        """
        return {}

    def set_params(self, **params):
        """
        Set parameters for the model.
        """
        return self
