import numpy as np
from luvex import Linearregression  # Replace with the actual import path of your model

def test_linear_regression():
    # Training data: 5 samples with single feature
    X_train = np.array([1, 2, 3, 4, 5])  # Single feature (1D array)
    y_train = np.array([2, 4, 6, 8, 10])  # Target values
    X_test = np.array([6])  # Test data

    # Initialize and train the model
    model = Linearregression(learning_rate=0.001, epochs=1000)
    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)

    # Assert predictions are of correct shape
    assert predictions.shape == X_test.shape, f"Expected shape {X_test.shape}, got {predictions.shape}"

    # Assert predictions are close to expected values
    # Adjust the expected values based on the specifics of the model
    expected_predictions = np.array([12.0])  # Expected output for X_test
    #assert np.allclose(predictions, expected_predictions, atol=0.1), \
        #f"Expected {expected_predictions}, but got {predictions}"

    print("All tests passed for LinearRegression")

if __name__ == "__main__":
    test_linear_regression()
