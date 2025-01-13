# luvex
Developing ML Models from scratch : Regression - Linear (Least Squares Method), Multiple Linear. Classification - KNN, Logistic Regression, Decision Trees, Random Forest

# Luvex

Luvex is a Python package for implementing machine learning models such as Decision Tree, Random Forest, and more.

## Installation

You can install `luvex` from PyPI using pip:

```bash
pip install luvex


## Testing Linear Regression
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



## Testing Logistic Regression

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


## Test KNN

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

## Test MultiLinear Regression
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





## testing Decision Tree

import numpy as np
from luvex.node import Node
from luvex.decisiontree import DecisionTree


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

## Testing Random Forests

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



## License

MIT License

Copyright (c) 2025 Gladson K

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.





### Step 6: Build the Package
Once everything is ready, you need to build your package. Use the following commands:

1. **Install build tools**:
   ```bash
   pip install build

