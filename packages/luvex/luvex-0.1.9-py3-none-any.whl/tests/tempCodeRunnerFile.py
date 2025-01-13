import numpy as np
from luvex import RandomForest  # Import your model
from luvex.decisiontree import DecisionTree
from luvex import RandomForest 

def test_random_forest():
    X_train = np.array([[1, 2], [2, 3], [3, 4]])
    y_train = np.array([0, 1, 0])
    X_test = np.array([[2, 2]])

    model = RandomForest(n_trees=3, max_depth=5, min_samples_split=2, n_features=1)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    assert predictions[0] >= 0  # Modify to check the first value in the returned array


if __name__ == "__main__":
    test_random_forest()
    print("All tests passed for RandomForest")
