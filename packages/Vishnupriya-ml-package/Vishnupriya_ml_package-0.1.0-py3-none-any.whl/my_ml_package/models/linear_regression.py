import numpy as np
import plotly.express as px
import pickle

class LinearRegression:
    def __init__(self, learning_rate, convergence_tol=0.0001):
        self.learning_rate = learning_rate
        self.convergence_tol = convergence_tol
        self.W = None
        self.b = None

    def initialize_parameters(self, n_features):
        self.W = np.random.randn(n_features) * 0.01
        self.b = 0

    def forward(self, X):
        return np.dot(X, self.W) + self.b

    def compute_cost(self, predictions):
        m = len(predictions)
        cost = np.sum(np.square(predictions - self.y)) / (2 * m)
        return cost

    def backward(self, predictions):
        m = len(predictions)
        self.dW = np.dot(predictions - self.y, self.X) / m
        self.db = np.sum(predictions - self.y) / m

    def fit(self, X, y, iterations, plot_cost=True):
        self.X = X
        self.y = y
        self.initialize_parameters(X.shape[1])
        costs = []
        for i in range(iterations):
            predictions = self.forward(X)
            cost = self.compute_cost(predictions)
            self.backward(predictions)
            self.W -= self.learning_rate * self.dW
            self.b -= self.learning_rate * self.db
            costs.append(cost)

            if i % 100 == 0:
                print(f'Iteration: {i}, Cost: {cost}')

            if i > 0 and abs(costs[-1] - costs[-2]) < self.convergence_tol:
                print(f'Converged after {i} iterations.')
                break

        if plot_cost:
            fig = px.line(y=costs, title="Cost vs Iteration", template="plotly_dark")
            fig.update_layout(
                title_font_color="#41BEE9",
                xaxis=dict(color="#41BEE9", title="Iterations"),
                yaxis=dict(color="#41BEE9", title="Cost")
             )
            fig.show()

    def predict(self, X):
        return self.forward(X)

    def save_model(self, filename):
        model_data = {"W": self.W, "b": self.b}
        with open(filename, "wb") as file:
            pickle.dump(model_data, file)

    @classmethod
    def load_model(cls, filename):
        with open(filename, "rb") as file:
            model_data = pickle.load(file)
        model = cls()
        model.W = model_data["W"]
        model.b = model_data["b"]
        return model