import numpy as np
from collections import Counter
from sklearn.base import BaseEstimator
from luvex.node import Node  # Import the Node class
from luvex.decisiontree import DecisionTree

class RandomForest(BaseEstimator):
    def __init__(self, n_trees=10, max_depth=None, min_samples_split=2, n_features=None):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.n_features = n_features
        self.trees = []

    def _bootstrap_sample(self, X, y):
        n_samples = X.shape[0]
        indices = np.random.choice(n_samples, n_samples, replace=True)
        return X[indices], y[indices]

    def _subsample_features(self, X):
        n_features_total = X.shape[1]
        if self.n_features is None or self.n_features > n_features_total:
            self.n_features = n_features_total  # Use all features if not specified or exceeds the total
        features_indices = np.random.choice(n_features_total, self.n_features, replace=False)
        return features_indices


    def fit(self, X, y):
        self.trees = []
        for _ in range(self.n_trees):
        # Bootstrap sampling
            X_sample, y_sample = self._bootstrap_sample(X, y)

            if X_sample.shape[0] == 0 or len(y_sample) == 0:
                continue  # Skip invalid samples

        # Subsample features
            if self.n_features is None:
                self.n_features = int(np.sqrt(X.shape[1]))  # Default: sqrt(number of features)

        feature_indices = self._subsample_features(X_sample)

        # Train a Decision Tree
        tree = DecisionTree(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
        tree.fit(X_sample[:, feature_indices], y_sample)

        self.trees.append((tree, feature_indices))


    def predict(self, X):
        # Collect predictions from all trees
        tree_predictions = np.array([tree.predict(X[:, features]) for tree, features in self.trees])

        # Aggregate predictions (majority vote for classification)
        return np.apply_along_axis(self._majority_vote, axis=0, arr=tree_predictions)

    def _majority_vote(self, predictions):
        return Counter(predictions).most_common(1)[0][0]
    
    def predict_proba(self, X):
    
        n_samples = X.shape[0]
        n_classes = len(self.classes_)
        prob_matrix = np.zeros((n_samples, n_classes))

        for tree, features in self.trees:
            tree_predictions = tree.predict(X[:, features])
            for i, pred in enumerate(tree_predictions):
                class_idx = np.where(self.classes_ == pred)[0][0]
                prob_matrix[i, class_idx] += 1

        prob_matrix /= len(self.trees)  # Normalize to get probabilities
        return prob_matrix


    def get_params(self, deep=True):
        return {
            "n_trees": self.n_trees,
            "max_depth": self.max_depth,
            "min_samples_split": self.min_samples_split,
            "n_features": self.n_features
        }

    def set_params(self, **params):
        for param, value in params.items():
            setattr(self, param, value)
        return self
