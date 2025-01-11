import numpy as np


class My_Linear_Regression():  
    def __init__(self, learning_rate=0.01,epochs=1000): 
        """
        Initializes the linear regression model with the specified learning rate
        and number of epochs.

        Parameters:
            learning_rate (float): The step size for the gradient descent optimizer.
            epochs (int): The number of iterations to run the gradient descent.

        Attributes:
            learning_rate (float): The learning rate for gradient descent.
            weights (None or np.ndarray): The weights of the model, initialized as None.
            bias (None or float): The bias term of the model, initialized as None.
            cost_history (list): A list to store the history of cost values during training.
            epochs (int): The number of iterations for which the model will be trained.
        """

        self.learning_rate = learning_rate
        self.weights = None  
        self.bias = None        
        self.cost_history = []
        self.epochs=epochs
    
    def hypothesis(self, X):

        """
        Hypothesis function for linear regression, given by
        h(x) = w * x + b
        where w is the weight, b is the bias term, and x is the input variable.
        """
        return  self.weights * X + self.bias
    
    def cost_function(self, X, y):
        
        """
        Cost function for linear regression, given by
        J(θ) = (1/2m) * Σ(h(x) - y)²
        where h(x) is the hypothesis, m is the number of samples, and y is the target variable.
        """
        
        m = len(y)
        predictions = self.hypothesis(X)

        #J(θ) = (1/2m) * Σ(h(x) - y)²
        
        cost = (1/(2*m)) * np.sum((predictions - y) ** 2)
        return cost
    
    def gradient_descent(self, X, y):
        
        """
        Gradient descent function for linear regression.
        
        Parameters
        ----------
        X (np.ndarray): The input features of shape (n_samples, n_features).
        y (np.ndarray): The target variable of shape (n_samples,).
        
        """
        
        m = len(y)
        predictions = self.hypothesis(X)
        error = predictions - y
        
        
        # ∂J/∂m = (1/m) * Σ(h(x) - y) * x
        # ∂J/∂b = (1/m) * Σ(h(x) - y)

        dw = (1/m) * np.sum(error * X)
        db = (1/m) * np.sum(error)


        self.weights -= self.learning_rate * dw
        self.bias -= self.learning_rate * db
    
    def fit(self, X, y):
       
        """
        Fits the linear regression model to the training data using gradient descent.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data.
        y : array-like, shape (n_samples,)
            Target values.

        This method initializes the model parameters (weights and bias) to zero and performs 
        gradient descent for the specified number of epochs. In each epoch, it updates the 
        model parameters by calling the gradient descent method and calculates the cost using 
        the cost function. The cost for each epoch is stored in the cost_history attribute.
        """

        X = np.array(X)
        y = np.array(y)
        
        
        self.weights = 0
        self.bias = 0
        
        for _ in range(self.epochs):
            self.gradient_descent(X, y)
            cost = self.cost_function(X, y)
            self.cost_history.append(cost)
    

    def predict(self, X):
        
        """
        Predicts the target values for the given input data.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Input data for which to predict the target values.

        Returns
        -------
        np.ndarray
            Predicted target values for each input sample.
        """

        X = np.array(X)
        return self.hypothesis(X)
    
    def get_params(self):
        """
        Returns the model parameters (weights and bias) as a tuple.

        Returns
        -------
        tuple
            A tuple containing the weights and bias of the model.
        """
        return self.weights, self.bias
