import numpy as np
import plotly.express as px

class MultivariateRegression:
    def __init__(self, learning_rate=0.01, convergence_tol=0.0001):
        self.learning_rate = learning_rate
        self.convergence_tol = convergence_tol
        self.W = None  # Weights (one for each feature)
        self.b = None  # Bias term (scalar)

    def initialize_parameters(self, n_features):
        """Initialize weights and bias."""
        self.W = np.random.randn(n_features) * 0.01  # Small random weights
        self.b = 0  # Bias initialized to 0

    def forward(self, X):
        """Compute predictions using the linear model."""
        return np.dot(X, self.W) + self.b

    def compute_cost(self, predictions, y):
        """Compute Mean Squared Error (MSE) cost."""
        m = len(y)  # Number of samples
        return np.sum(np.square(predictions - y)) / (2 * m)

    def backward(self, predictions, X, y):
        """Compute gradients for weights and bias."""
        m = len(y)  # Number of samples
        dW = np.dot(X.T, (predictions - y)) / m  # Gradient of W
        db = np.sum(predictions - y) / m  # Gradient of b
        return dW, db

    def fit(self, X, y, iterations=1000, plot_cost=True):
        """Train the model using Gradient Descent."""
        # Initialize parameters
        n_features = X.shape[1]
        self.initialize_parameters(n_features)

        costs = []  # To track cost over iterations

        for i in range(iterations):
            # Forward pass
            predictions = self.forward(X)

            # Compute cost
            cost = self.compute_cost(predictions, y)

            # Backward pass (gradient computation)
            dW, db = self.backward(predictions, X, y)

            # Update parameters
            self.W -= self.learning_rate * dW
            self.b -= self.learning_rate * db

            # Store cost for visualization
            costs.append(cost)

            # Print progress
            if i % 100 == 0:
                print(f"Iteration {i}, Cost: {cost:.4f}")

            # Check convergence
            if i > 0 and abs(costs[-1] - costs[-2]) < self.convergence_tol:
                print(f"Converged after {i} iterations.")
                break

        # Plot cost over iterations
        if plot_cost:
            fig = px.line(y=costs, title="Cost vs Iterations", template="plotly_dark")
            fig.update_layout(
                title_font_color="#41BEE9",
                xaxis=dict(color="#41BEE9", title="Iterations"),
                yaxis=dict(color="#41BEE9", title="Cost")
            )
            fig.show()

    def predict(self, X):
        """Predict outputs for the given input data."""
        return self.forward(X)

