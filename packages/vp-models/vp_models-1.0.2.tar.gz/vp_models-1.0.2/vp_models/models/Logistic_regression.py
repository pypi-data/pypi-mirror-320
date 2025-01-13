import numpy as np
import plotly.express as px

class Logistic_regression:

    def __init__(self, learning_rate=0.0001, epochs=1000):
        np.random.seed(1)
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights = None
        self.bias = None
        self.cost_history = []

    def forward(self, X):
        """ Compute the forward pass (hypothesis function) """
        return 1 / (1 + np.exp(-(np.dot(X, self.weights) + self.bias)))

    def compute_cost(self, X, Y):
        """ Compute the cost function for logistic regression: J(θ) """
        m = len(Y)
        predictions = self.forward(X)
        # J(θ) = (-1/m) * Σ(y*log(h(x)) + (1-y)*log(1-h(x)))
        cost = (-1/m) * np.sum(Y * np.log(predictions + 1e-8) + (1 - Y) * np.log(1 - predictions + 1e-8))
        return cost

    def backward(self, X, Y):
        """ Perform backward pass (compute gradients and update weights/bias) """
        m = len(Y)
        predictions = self.forward(X)
        error = predictions - Y
        
        dw = (1/m) * np.dot(X.T, error)
        db = (1/m) * np.sum(error)
        
        self.weights -= self.learning_rate * dw
        self.bias -= self.learning_rate * db

    def fit(self, X, Y):
        """ Fit the model using gradient descent """
        X = np.array(X)
        Y = np.array(Y)

        n_features = X.shape[1]
        self.weights = np.zeros(n_features)
        self.bias = 0

        for epoch in range(self.epochs):
            self.backward(X, Y)
            cost = self.compute_cost(X, Y)
            self.cost_history.append(cost)

            # Print cost for every 100 iterations
            if epoch % 100 == 0:
                print(f"Cost after epoch {epoch}: {cost}")

    def predict(self, X):
        """ Predict binary labels based on the learned model """
        predictions = self.forward(X)
        predictions = np.where(predictions > 0.5, 1, 0)  # 0.5 threshold for binary classification
        return predictions

    def get_params(self):
        """ Get model parameters (weights and bias) """
        return self.weights, self.bias

    # def plot_cost_history(self):
    #     """ Plot the cost history vs. epochs """
    #     fig = px.line(y=self.cost_history, title="Cost vs Epochs", template="plotly_dark")
    #     fig.update_layout(
    #         title_font_color="#41BEE9",
    #         xaxis=dict(color="#41BEE9", title="Epochs"),
    #         yaxis=dict(color="#41BEE9", title="Cost")
    #     )
    #     fig.show()
