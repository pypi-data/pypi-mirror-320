import numpy as np

class LinearRegression:
    def __init__(self, x, y):
        self.data = x
        self.label = y
        self.m = 0
        self.b = 0
        self.n = len(x)

    def fit(self, epochs, lr):
        for i in range(epochs):
            y_pred = self.m * self.data + self.b
            D_m = (-2 / self.n) * sum(self.data * (self.label - y_pred))
            D_b = (-1 / self.n) * sum(self.label - y_pred)
            self.m = self.m - lr * D_m
            self.b = self.b - lr * D_b

    def predict(self, inp):
        return self.m * inp + self.b
