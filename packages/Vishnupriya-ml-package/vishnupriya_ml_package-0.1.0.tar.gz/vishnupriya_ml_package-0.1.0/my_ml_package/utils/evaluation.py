from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

class Evaluator:
    @staticmethod
    def evaluate_classification(y_true, y_pred):
        """
        Evaluates classification performance using accuracy.
        """
        accuracy = accuracy_score(y_true, y_pred)
        return {"accuracy": accuracy}

    @staticmethod
    def evaluate_regression(y_true, y_pred):
        """
        Evaluates regression performance using MSE and R2 score.
        """
        mse = mean_squared_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        return {"mse": mse, "r2_score": r2}
