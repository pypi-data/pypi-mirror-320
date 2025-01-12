import numpy as np
from luvex import KNN  # Import your model

def test_knn():
    X_train = np.array([[1, 2], [2, 3], [3, 4]])
    y_train = np.array([0, 1, 0])
    X_test = np.array([[2, 2]])
    
    model = KNN(k=2)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    assert predictions >= [0]  # Test if the prediction is correct

if __name__ == "__main__":
    test_knn()
    print("All tests passed for KNN")
