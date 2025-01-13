import numpy as np
from luvex import DecisionTree  # Import your model

def test_decision_tree():
    X_train = np.array([[1, 2], [2, 3], [3, 4]])
    y_train = np.array([0, 1, 0])
    X_test = np.array([[2, 2]])

    model = DecisionTree()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    assert predictions[0] >= 1  # Fix the expected prediction here based on your model



if __name__ == "__main__":
    test_decision_tree()
    print("All tests passed for DecisionTree")
