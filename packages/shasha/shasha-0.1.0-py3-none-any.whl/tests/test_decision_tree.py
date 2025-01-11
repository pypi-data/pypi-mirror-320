import numpy as np
from shasha import My_DecisionTree

def test_decision_tree():
    X_train = np.array([[1, 2], [2, 3], [3, 4]])
    y_train = np.array([0, 1, 0])
    X_test = np.array([[2, 2]])
    model = My_DecisionTree()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    assert predictions == 0

if __name__ == "__main__":
    test_decision_tree()
    print("All tests passed for My_DecisionTree")
