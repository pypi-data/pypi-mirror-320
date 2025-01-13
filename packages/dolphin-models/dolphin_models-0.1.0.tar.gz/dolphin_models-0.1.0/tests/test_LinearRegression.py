import numpy as np
from dolphin_models import LinearRegression


def test_linear_regression():
    X_train = np.array([[1], [2], [3], [4]])
    y_train = np.array([2, 4, 6, 8])
    X_test = np.array([[5]])

    model = LinearRegression()
    model.scr_fit(X_train, y_train)
    predictions = model.scr_predict(X_test)

    assert np.isclose(predictions[0], 10), f"Expected 10, but got {predictions[0]}"


if __name__ == "__main__":
    test_linear_regression()
    print("All tests passed for LinearRegression")
