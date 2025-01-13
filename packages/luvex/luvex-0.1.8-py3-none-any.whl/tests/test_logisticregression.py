import numpy as np
from luvex import Logisticregression  # Replace with your actual import path

def test_logistic_regression():
    # Training data: 3 samples with 2 features each
    X_train = np.array([[1, 2], [2, 3], [3, 4]])
    y_train = np.array([0, 1, 0])
    X_test = np.array([[2, 3]])
    y_test = np.array([1])

    # Initialize and train the model
    model = Logisticregression(learn_rate=0.01, n_iter=1000, verbose=True)
    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)
    print(f"Predictions: {predictions}")

    # Assert predictions are binary (0 or 1)
    assert np.all(np.isin(predictions, [0, 1])), "Predictions should be binary."

    # Evaluate accuracy
    acc = model.accu_score(X_test, y_test)
    print(f"Test Accuracy: {acc:.2f}")

if __name__ == "__main__":
    test_logistic_regression()
    print("All tests passed for Logisticregression")
