import numpy as np
from dolphin_models import LogisticRegression


def test_logistic_regression():
    X_train = np.array([[1], [2], [3], [4]])
    y_train = np.array([0, 0, 1, 1])
    X_test = np.array([[2.5]])

    model = LogisticRegression()
    model.scr_fit(X_train, y_train)
    predictions = model.scr_predict(X_test)

    assert predictions[0] in [0, 1], f"Expected 0 or 1, but got {predictions[0]}"


if __name__ == "__main__":
    test_logistic_regression()
    print("All tests passed for LogisticRegression")
