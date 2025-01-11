import numpy as np
from shasha import My_Multiple_Regression

def test_multiple_regression():
    X = np.array([[1, 2], [2, 3], [3, 4]])
    y = np.array([1, 2, 3])
    model = My_Multiple_Regression()
    model.fit(X, y)
    predictions = model.predict(X)
    assert np.allclose(predictions, y)

if __name__ == "__main__":
    test_multiple_regression()
    print("All tests passed for My_Multiple_Regression")
