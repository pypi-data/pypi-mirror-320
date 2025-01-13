import numpy as np
from luvex import MultipleLinear  # Replace with your actual import

def test_multiple_linear():
    # Training data: 3 samples with 2 features each
    X_train = np.array([[1, 2], [2, 3], [3, 4]])
    y_train = np.array([1, 2, 3]).reshape(-1, 1)  # Reshape to column vector
    X_test = np.array([[2, 3], [3, 4]])  # Test data
    y_test = np.array([2, 3]).reshape(-1, 1)

    # Initialize and train the model
    model = MultipleLinear(learning_rate=0.01, iterations=1000)
    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)

    # Assert predictions are of correct shape
    assert predictions.shape == y_test.shape, f"Expected shape {y_test.shape}, got {predictions.shape}"

    # Evaluate the model
    mse = model.score(X_test, y_test)
    print(f"Predictions: {predictions.flatten()}")
    print(f"Mean Squared Error: {mse}")

    # Assert that MSE is within a reasonable range
    assert mse < 0.1, f"High Mean Squared Error: {mse}"

if __name__ == "__main__":
    test_multiple_linear()
    print("All tests passed for MultipleLinear")
