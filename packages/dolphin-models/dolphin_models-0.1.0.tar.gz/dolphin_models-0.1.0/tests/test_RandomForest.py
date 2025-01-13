import numpy as np
from dolphin_models import RandomForest


def test_random_forest():
    # Training data
    X_train = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
    y_train = np.array([1, 0, 1, 0])

    # Test data
    X_test = np.array([[3, 3], [4, 5]])

    # Initialize and train the Random Forest model
    model = RandomForest()
    model.scr_fit(X_train, y_train)

    # Make predictions
    predictions = model.scr_predict(X_test)

    # Assertions to check predictions
    assert len(predictions) == len(X_test), f"Expected {len(X_test)} predictions, but got {len(predictions)}"
    assert predictions[0] in [0, 1], f"Expected prediction in [0, 1], but got {predictions[0]}"
    assert predictions[1] in [0, 1], f"Expected prediction in [0, 1], but got {predictions[1]}"


if __name__ == "__main__":
    test_random_forest()
    print("All tests passed for RandomForest")
