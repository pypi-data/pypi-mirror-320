import numpy as np
from luvex import Linearregression  # Import your model

def test_linear_regression():
    X_train = np.array([1, 2, 3])
    y_train = np.array([1, 2, 3])
    X_test = np.array([2])
    
    model = Linearregression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    assert np.allclose(predictions, np.array([2]))  # Test if prediction matches expected value

if __name__ == "__main__":
    test_linear_regression()
    print("All tests passed for Linearregression")
