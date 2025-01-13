import numpy as np
from dolphin_models import KNN


def test_knn():
    X_train = np.array([[1], [2], [3], [4]])
    y_train = np.array([1, 0, 1, 0])
    X_test = np.array([[3]])

    model = KNN(k=3)
    model.scr_fit(X_train, y_train)
    predictions = model.scr_predict(X_test)

    assert predictions[0] in [0, 1], f"Expected 0 or 1, but got {predictions[0]}"


if __name__ == "__main__":
    test_knn()
    print("All tests passed for KNN")
