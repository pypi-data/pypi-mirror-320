from sklearn.base import BaseEstimator
import numpy as np
from luvex.node import Node  # Import the Node class
from collections import Counter
#from luvex.node import Node  # Import Node class

class DecisionTree(BaseEstimator):
    def __init__(self, min_samples_split=2, max_depth=100, n_features=None):
        self.min_samples_split = min_samples_split
        self.max_depth = max_depth
        self.n_features = n_features
        self.root = None

    def fit(self, X, y):
        self.root = self._grow_tree(X, y)

    def _grow_tree(self, X, y, depth=0):
        n_samples, n_features = X.shape
        n_labels = len(np.unique(y))

        # Stop criteria
        if depth >= self.max_depth or n_labels == 1 or n_samples < self.min_samples_split:
            leaf_value = self._most_common_label(y)
            return Node(value=leaf_value)  # Use the Node class here

        # Find the best split
        best_feature, best_thresh = self._best_split(X, y)
        if best_feature is None or best_thresh is None:  # No valid split
            leaf_value = self._most_common_label(y)
            return Node(value=leaf_value)

        # Split data
        left_idxs, right_idxs = self._split(X[:, best_feature], best_thresh)
        left = self._grow_tree(X[left_idxs, :], y[left_idxs], depth + 1)
        right = self._grow_tree(X[right_idxs, :], y[right_idxs], depth + 1)
        return Node(best_feature, best_thresh, left, right)

    def _best_split(self, X, y):
        n_samples, n_features = X.shape
        if n_samples <= 1:
            return None, None

        best_gain = -float("inf")
        split_feature, split_threshold = None, None

        for feature in range(n_features):
            X_column = X[:, feature]
            thresholds = np.unique(X_column)
            for threshold in thresholds:
                gain = self._information_gain(y, X_column, threshold)

                if gain > best_gain:
                    best_gain = gain
                    split_feature = feature
                    split_threshold = threshold

        return split_feature, split_threshold

    def _information_gain(self, y, X_col, thr):
        # get the parent entropy
        parent_ent = self._entropy(y)

        # create child Node
        left_idx, right_idx = self._split(X_col, thr)

        if len(left_idx) == 0 or len(right_idx) == 0:
            return 0

        # calculate the weighted entropy of child Node
        n = len(y)
        n_le, n_ri = len(left_idx), len(right_idx)
        e_le, e_ri = self._entropy(y[left_idx]), self._entropy(y[right_idx])

        child_ent = (n_le / n) * (e_le) + (n_ri / n) * (e_ri)  # weighted average

        # calculate the Information Gain
        inform_gain = parent_ent - child_ent

        return inform_gain

    def _split(self, X_col, thr):
        left_idxs = np.argwhere(X_col <= thr).flatten()
        right_idxs = np.argwhere(X_col > thr).flatten()
        return left_idxs, right_idxs

    def _entropy(self, y):
        hist = np.bincount(y)
        p_x = hist / len(y)
        return -np.sum([p * np.log2(p) for p in p_x if p > 0])

    def _most_common_label(self, y):
        counter = Counter(y)
        value = counter.most_common(1)[0][0]
        return value

    def _traverse_tree(self, x, node):
        if node.is_leaf_node():
            return node.value

        if x[node.feature] <= node.threshold:
            return self._traverse_tree(x, node.left)
        else:
            return self._traverse_tree(x, node.right)

    def predict(self, X):
        return np.array([self._traverse_tree(x, self.root) for x in X])

    def get_params(self, deep=True):
        # Return hyperparameters as a dictionary
        return {
            "min_samples_split": self.min_samples_split,
            "max_depth": self.max_depth,
            "n_features": self.n_features
        }

    def set_params(self, **params):
        # Set hyperparameters
        for param, value in params.items():
            setattr(self, param, value)
        return self
