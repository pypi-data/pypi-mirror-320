import numpy as np

class My_Logistic_Regression():

  def __init__(self, learning_rate=0.001, epochs=1000):

    self.learning_rate = learning_rate
    self.weights= None
    self.bias = None
    self.cost_history = []
    self.epochs=epochs

  # sigmoid function for hypothesis

  def hypothesis(self, X):
    return 1 / (1 + np.exp( - (X.dot(self.weights) + self.bias)))
  
  def cost_function(self,X,Y):

    m=len(Y)
    predictions = self.hypothesis(X)

    # J(θ) = (-1/m) * Σ(y*log(h(x)) + (1-y)*log(1-h(x)))
    cost = (-1/m)*np.sum(Y*np.log(predictions) + (1-Y)*np.log(1-predictions))
    return cost
  
  def gradient_descent(self,X,y):
    
    m=len(y)
    predictions = self.hypothesis(X)
    error = predictions - y

    dw = (1/m)*np.dot(X.T, error)
    db = (1/m)*np.sum(error)

    self.weights -= self.learning_rate * dw
    self.bias -= self.learning_rate * db


  def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        
        n_features = X.shape[1]

        self.weights = np.zeros(n_features)
        self.bias = 0

        for i in range(self.epochs):
            self.gradient_descent(X,y)
            cost=self.cost_function(X,y)
            self.cost_history.append(cost)


  def predict(self, X):
    Y_pred=self.hypothesis(X)
    Y_pred=np.where(Y_pred>0.5,1,0)
    return Y_pred

  def get_params(self):
        return self.weights, self.bias
  