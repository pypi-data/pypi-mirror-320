import numpy as np
import plotly.express as px

class Linear_regression:

    def __init__(self, learning_rate=0.01, convergence_tol=0.0001, epochs=1000):
        self.learning_rate = learning_rate
        self.convergence_tol = convergence_tol
        self.epochs = epochs
        self.W = None  # Weights of the model
        self.b = None  # Bias of the model

    def initialize_parameters(self, n_features):
        """ Initialize weights and bias. """
        self.W = np.random.randn(n_features) * 0.01  # Small random values
        self.b = 0  # Bias initialized to zero

    def forward(self, X):
        """ Linear equation: y = X * W + b """
        return X * self.W + self.b  # Element-wise multiplication for prediction

    def compute_cost(self, predictions):
        """ Calculate the cost using Mean Squared Error. """
        m = len(predictions)
        cost = np.sum(np.square(predictions - self.y)) / (2 * m)
        return cost

    def backward(self, predictions):
        """ Calculate gradients for the weights and bias. """
        m = len(predictions)
        self.dW = np.sum((predictions - self.y) * self.X) / m  # Element-wise multiplication
        self.db = np.sum(predictions - self.y) / m

    def fit(self, X, y, plot_cost=True):
        """
        Fit the model using gradient descent to minimize the cost function.
        """
        self.X = X
        self.y = y
        self.initialize_parameters(X.shape[1])  # Initialize with number of features
        costs = []

        for i in range(self.epochs):
            predictions = self.forward(X)
            cost = self.compute_cost(predictions)
            self.backward(predictions)

            # Update parameters
            self.W -= self.learning_rate * self.dW
            self.b -= self.learning_rate * self.db
            costs.append(cost)

            if i % 100 == 0:
                print(f'Iteration: {i}, Cost: {cost}')

            # Check convergence
            if i > 0 and abs(costs[-1] - costs[-2]) < self.convergence_tol:
                print(f'Converged after {i} iterations.')
                break

        # Plot cost vs iterations
        # if plot_cost:
        #     fig = px.line(y=costs, title="Cost vs Iteration", template="plotly_dark")
        #     fig.update_layout(
        #         title_font_color="#41BEE9",
        #         xaxis=dict(color="#41BEE9", title="Iterations"),
        #         yaxis=dict(color="#41BEE9", title="Cost")
        #     )
        #     fig.show()

    def predict(self, X):
        """ Make predictions using the learned weights and bias. """
        X = np.array(X)
        return self.forward(X)

    def get_params(self):
        """ Returns the model parameters (weights and bias). """
        return self.W, self.b
