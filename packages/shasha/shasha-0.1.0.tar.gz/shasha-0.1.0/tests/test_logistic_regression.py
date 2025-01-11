import numpy as np
from shasha import My_Logistic_Regression

def test_logistic_regression():
    X = np.array([[1, 2], [2, 3], [3, 4]])
    y = np.array([0, 1, 0])
    model = My_Logistic_Regression()
    model.fit(X, y)
    predictions = model.predict(X)
    assert np.allclose(predictions, y)

if __name__ == "__main__":
    test_logistic_regression()
    print("All tests passed for My_Logistic_Regression")
