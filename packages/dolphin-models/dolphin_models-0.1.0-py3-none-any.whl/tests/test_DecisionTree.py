import numpy as np
from dolphin_models import DecisionTree


def test_decision_tree():
    # Training data
    X_train = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    y_train = np.array([0, 1, 0, 1])

    # Test data
    X_test = np.array([[3, 3], [1, 2]])

    # Initialize and train the Decision Tree model
    model = DecisionTree()
    model.scr_fit(X_train, y_train)

    # Make predictions
    predictions = model.scr_predict(X_test)

    # Assertions to check predictions
    assert len(predictions) == len(X_test), f"Expected {len(X_test)} predictions, but got {len(predictions)}"
    assert predictions[0] in [0, 1], f"Expected prediction in [0, 1], but got {predictions[0]}"
    assert predictions[1] in [0, 1], f"Expected prediction in [0, 1], but got {predictions[1]}"


if __name__ == "__main__":
    test_decision_tree()
    print("All tests passed for DecisionTree")
