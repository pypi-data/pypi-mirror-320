from .Linear_regression import Linear_regression
from .Multivariate_regression import Multivariate_regression
from .Logistic_regression import Logistic_regression
from .Knn import Knn_
from .Decision_tree import Decision_tree
from .Random_forest import Random_forest

# Define what will be imported when using `from models import *`
__all__ = [
    "Linear_regression",
    "Multivariate_regression",
    "Logistic_regression",
    "Knn_",
    "Decision_tree",
    "Random_forest",
]