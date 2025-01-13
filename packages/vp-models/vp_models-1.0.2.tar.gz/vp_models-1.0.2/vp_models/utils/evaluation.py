from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score, explained_variance_score
)

class Evaluator:
    @staticmethod
    def evaluate_linear_regression(y_true, y_pred):
        """
        Evaluates linear regression performance using MSE, MAE, R2 score, and explained variance.
        """
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        evs = explained_variance_score(y_true, y_pred)
        return {"mse": mse, "mae": mae, "r2_score": r2, "explained_variance": evs}

    @staticmethod
    def evaluate_logistic_regression(y_true, y_pred, y_pred_proba=None):
        """
        Evaluates logistic regression performance using accuracy, precision, recall, F1 score, and optionally ROC AUC.
        """
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='binary')
        recall = recall_score(y_true, y_pred, average='binary')
        f1 = f1_score(y_true, y_pred, average='binary')
        metrics = {"accuracy": accuracy, "precision": precision, "recall": recall, "f1_score": f1}
        if y_pred_proba is not None:  # Requires probabilities for positive class
            auc = roc_auc_score(y_true, y_pred_proba)
            metrics["roc_auc"] = auc
        return metrics

    @staticmethod
    def evaluate_multivariate_regression(y_true, y_pred):
        """
        Evaluates multivariate regression performance using MSE, MAE, and R2 score for each target variable.
        """
        mse = mean_squared_error(y_true, y_pred, multioutput='raw_values')
        mae = mean_absolute_error(y_true, y_pred, multioutput='raw_values')
        r2 = r2_score(y_true, y_pred, multioutput='raw_values')
        return {"mse_per_target": mse, "mae_per_target": mae, "r2_score_per_target": r2}

    @staticmethod
    def evaluate_knn(y_true, y_pred, task="classification"):
        """
        Evaluates k-NN performance.
        - For classification: accuracy, precision, recall, F1 score.
        - For regression: MSE, MAE, and R2 score.
        """
        if task == "classification":
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, average='weighted')
            recall = recall_score(y_true, y_pred, average='weighted')
            f1 = f1_score(y_true, y_pred, average='weighted')
            return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1_score": f1}
        elif task == "regression":
            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            return {"mse": mse, "mae": mae, "r2_score": r2}

    @staticmethod
    def evaluate_decision_tree(y_true, y_pred, task="classification"):
        """
        Evaluates decision tree performance for classification or regression.
        """
        if task == "classification":
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, average='weighted')
            recall = recall_score(y_true, y_pred, average='weighted')
            f1 = f1_score(y_true, y_pred, average='weighted')
            return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1_score": f1}
        elif task == "regression":
            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            return {"mse": mse, "mae": mae, "r2_score": r2}

    @staticmethod
    def evaluate_random_forest(y_true, y_pred, task="classification"):
        """
        Evaluates random forest performance for classification or regression.
        """
        if task == "classification":
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, average='weighted')
            recall = recall_score(y_true, y_pred, average='weighted')
            f1 = f1_score(y_true, y_pred, average='weighted')
            return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1_score": f1}
        elif task == "regression":
            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            return {"mse": mse, "mae": mae, "r2_score": r2}
