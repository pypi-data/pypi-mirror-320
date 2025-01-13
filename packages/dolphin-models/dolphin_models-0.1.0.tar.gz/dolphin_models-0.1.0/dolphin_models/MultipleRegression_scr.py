import numpy as np


class MultipleRegression:
    def __init__(self, learning_rate=0.01,epochs=1000):
        self.learning_rate = learning_rate
        self.weights = None
        self.bias = None
        self.cost_history = []
        self.epochs=epochs

    
    def hypothesis(self, X):

        return np.dot(X, self.weights) + self.bias
    
    def cost_function(self, X, y):

        m = len(y)
        predictions = self.hypothesis(X)
       
        # J(θ) = (1/2m) * Σ(h(x) - y)²
       
        cost = (1/(2*m)) * np.sum((predictions - y) ** 2)
        return cost
    
    def gradient_descent(self, X, y):
        
        m = len(y)
        predictions = self.hypothesis(X)
        error = predictions - y
        
        # ∂J/∂m = (1/m) * X.T * (h(x) - y)
        # ∂J/∂b = (1/m) * Σ(h(x) - y
        
        dw = (1/m) * np.dot(X.T, error)
        db = (1/m) * np.sum(error)

        self.weights -= self.learning_rate * dw
        self.bias -= self.learning_rate * db
    
    def scr_fit(self, X, y):
        
        X = np.array(X)
        y = np.array(y)
        
        n_features = X.shape[1]

        self.weights = np.zeros(n_features)
        self.bias = 0
        
        for _ in range(self.epochs):
            self.gradient_descent(X, y)
            cost = self.cost_function(X, y)
            self.cost_history.append(cost)

    
    def scr_predict(self, X):
        X = np.array(X)
        return self.hypothesis(X)
    
    
    def get_params(self):
        return self.weights, self.bias
    

