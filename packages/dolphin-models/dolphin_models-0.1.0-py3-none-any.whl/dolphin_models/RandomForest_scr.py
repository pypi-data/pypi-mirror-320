from .DecisionTree_scr import DecisionTree
from collections import Counter
import numpy as np


class RandomForest:
    def __init__(self, n_trees=10, min_samples_split=2, max_depth=100, n_features=None):
        self.n_trees = n_trees
        self.trees = []
        self.min_samples_split = min_samples_split
        self.max_depth = max_depth
        self.n_features = n_features

    def scr_fit(self, X, y):
        self.trees = []
        n_samples = X.shape[0]

        for _ in range(self.n_trees):
            # Bootstrap sampling: Randomly sample data with replacement
            indices = np.random.choice(n_samples, size=n_samples, replace=True)
            X_sample = X[indices]
            y_sample = y[indices]

            # Train a decision tree on the sampled data
            tree = DecisionTree(
                min_samples_split=self.min_samples_split,
                max_depth=self.max_depth,
                n_features=self.n_features
            )
            tree.scr_fit(X_sample, y_sample)
            self.trees.append(tree)

    def scr_predict(self, X):
        # Collect predictions from all trees
        tree_predictions = np.array([tree.scr_predict(X) for tree in self.trees])
        
        # Majority voting: Take the most common label for classification
        # Axis 0: Trees, Axis 1: Data points
        predictions = [Counter(tree_predictions[:, i]).most_common(1)[0][0] for i in range(X.shape[0])]
        return np.array(predictions)
