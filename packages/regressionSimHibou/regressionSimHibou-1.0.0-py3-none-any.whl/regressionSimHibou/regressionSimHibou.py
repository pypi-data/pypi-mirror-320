# simple_linear_regression.py

import numpy as np

class SimpleLinearRegression:
    def __init__(self):
        self.slope = 0
        self.intercept = 0

    def fit(self, X, y, learning_rate=0.01, epochs=1000):
        n = len(X)
        for _ in range(epochs):
            y_pred = self.slope * X + self.intercept
            # Calculate the gradients
            gradient_slope = (-2/n) * np.sum(X * (y - y_pred))
            gradient_intercept = (-2/n) * np.sum(y - y_pred)
            # Update parameters
            self.slope -= learning_rate * gradient_slope
            self.intercept -= learning_rate * gradient_intercept

    def predict(self, X):
        return self.slope * X + self.intercept

    def score(self, X, y):
        y_pred = self.predict(X)
        # Calculate R-squared value
        ss_total = np.sum((y - np.mean(y)) ** 2)
        ss_residual = np.sum((y - y_pred) ** 2)
        return 1 - (ss_residual / ss_total)
