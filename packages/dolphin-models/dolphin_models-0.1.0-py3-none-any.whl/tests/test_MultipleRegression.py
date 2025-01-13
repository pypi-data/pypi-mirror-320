import numpy as np
from dolphin_models import MultipleRegression


def test_multivariate_regression():
    X_train = np.array([[1, 2], [2, 3], [3, 4]])
    y_train = np.array([3, 5, 7])
    X_test = np.array([[4, 5]])

    model = MultipleRegression()
    model.scr_fit(X_train, y_train)
    predictions = model.scr_predict(X_test)

    assert np.isclose(predictions[0], 9), f"Expected 9, but got {predictions[0]}"


if __name__ == "__main__":
    test_multivariate_regression()
    print("All tests passed for MultipleRegression")
