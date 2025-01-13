import numpy as np
from luvex import MultipleLinear  # Import your model

def test_multiple_linear():
    X_train = np.array([[1, 2], [2, 3], [3, 4]])  # Example with two features
    y_train = np.array([1, 2, 3]).reshape(-1, 1)  # Ensure y_train is a 2D array (column vector)
    X_test = np.array([[2, 3]])  # Test sample

    model = MultipleLinear(learning_rate=0.01, iterations=1000)
    model.fit(X_train, y_train)
    predictions = model.predict()

    assert np.allclose(predictions, np.array([2]))  # Ensure predictions match expected value



if __name__ == "__main__":
    test_multiple_linear()
    print("All tests passed for MultipleLinear")
