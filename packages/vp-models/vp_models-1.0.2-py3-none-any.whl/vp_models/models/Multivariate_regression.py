import numpy as np
import plotly.express as px

class Multivariate_regression:
    def __init__(self, learning_rate=0.01, epochs=1000, convergence_tol=0.0001):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.convergence_tol = convergence_tol
        self.weights = None
        self.bias = None
        self.cost_history = []

    def forward(self, X):
        """Compute predictions using the linear model (hypothesis)."""
        return np.dot(X, self.weights) + self.bias

    def compute_cost(self, X, y):
        """Compute Mean Squared Error (MSE) cost."""
        m = len(y)  # Number of samples
        predictions = self.forward(X)
        # J(θ) = (1/2m) * Σ(h(x) - y)²
        cost = (1 / (2 * m)) * np.sum((predictions - y) ** 2)
        return cost

    def backward(self, X, y):
        """Compute gradients for weights and bias."""
        m = len(y)  # Number of samples
        predictions = self.forward(X)
        error = predictions - y

        # Gradients of weights and bias
        dw = (1 / m) * np.dot(X.T, error)  # Gradient of W
        db = (1 / m) * np.sum(error)  # Gradient of b
        
        return dw, db

    def fit(self, X, y):
        """Train the model using Gradient Descent."""
        # Initialize parameters
        X = np.array(X)
        y = np.array(y)
        n_features = X.shape[1]
        self.weights = np.zeros(n_features)
        self.bias = 0

        costs = []  # To track cost over iterations

        for epoch in range(self.epochs):
            # Backward pass (gradient computation)
            dw, db = self.backward(X, y)

            # Update parameters
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

            # Compute cost
            cost = self.compute_cost(X, y)
            costs.append(cost)

            # Print progress
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, Cost: {cost:.4f}")

            # Check convergence (if the change in cost is small)
            if epoch > 0 and abs(costs[-1] - costs[-2]) < self.convergence_tol:
                print(f"Converged after {epoch} epochs.")
                break

        # Plot cost over iterations
        # fig = px.line(y=costs, title="Cost vs Epochs", template="plotly_dark")
        # fig.update_layout(
        #     title_font_color="#41BEE9",
        #     xaxis=dict(color="#41BEE9", title="Epochs"),
        #     yaxis=dict(color="#41BEE9", title="Cost")
        # )
        # fig.show()

    def predict(self, X):
        """Predict outputs for the given input data."""
        return self.forward(X)

    def get_params(self):
        """Get model parameters (weights and bias)."""
        return self.weights, self.bias
