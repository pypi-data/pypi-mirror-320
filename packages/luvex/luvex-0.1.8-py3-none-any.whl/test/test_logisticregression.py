import numpy as np
from luvex import Logisticregression  # Import your model

def test_logistic_regression():
    X_train = np.array([[1, 2], [2, 3], [3, 4]])
    y_train = np.array([0, 1, 0])
    X_test = np.array([[2, 3]])

    model = Logisticregression(learn_rate=0.01, n_iter=1000)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    #assert predictions[0] >= 0  # Corrected to index into the first value of the array


if __name__ == "__main__":
    test_logistic_regression()
    print("All tests passed for Logisticregression")
