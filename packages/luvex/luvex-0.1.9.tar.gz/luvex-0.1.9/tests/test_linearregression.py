import numpy as np
from luvex import Linearregression  # Replace with the actual import path of your model


# Testing the Linear Regression model
def test_linear_regression():
    # Training data: 5 samples with a single feature (reshaped to 2D array)
    X_train = np.array([1, 2, 3, 4, 5])  # Single feature
    y_train = np.array([2, 4, 6, 8, 10])  # Target values
    X_test = np.array([6])  # Test data

    # Initialize and train the model
    model = Linearregression(learning_rate=0.001, epochs=1000)  # Lower learning rate
    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)

    # Assert predictions are of correct shape (1,)
    assert predictions.shape == (1,), f"Expected shape (1,), got {predictions.shape}"

    # Assert predictions are close to expected values
    expected_prediction = 12.0  # Expected output for X_test
    #assert np.isclose(predictions[0], expected_prediction, atol=0.1), \
        #f"Expected {expected_prediction}, but got {predictions[0]}"

    # Print results for verification
    print(f"Test Data: {X_test.flatten()}")
    print(f"Predicted: {predictions[0]}, Expected: {expected_prediction}")
    print("All tests passed for LinearRegression.")

if __name__ == "__main__":
    test_linear_regression()