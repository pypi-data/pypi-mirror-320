import numpy as np
from shasha import My_Linear_Regression

def test_linear_regression():
    X = np.array([[1], [2], [3]])
    y = np.array([1, 2, 3])
    model = My_Linear_Regression()
    model.fit(X, y)
    predictions = model.predict(X)
    assert np.allclose(predictions, y)

if __name__ == "__main__":
    test_linear_regression()
    print("All tests passed for My_Linear_Regression")
