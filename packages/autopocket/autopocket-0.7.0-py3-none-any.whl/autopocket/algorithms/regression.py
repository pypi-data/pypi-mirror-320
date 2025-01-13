import numpy as np
import pandas as pd
from scipy.stats import randint, uniform
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet, Lasso, LassoLars, LassoLarsIC, LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from autopocket.algorithms.base import BaseSearcher, EstimatorWrapper
from sklearn.dummy import DummyRegressor

class Regressor(BaseSearcher):
    """
        Class for regression models
        Inherits from EstimatorWrapper
        Includes DecisionTreeWrapper, RandomForestWrapper, LinearRegressionWrapper, LassoWrapper, ElasticNetWrapper
        Methods:
            fit(X,y) - fits the model
            predict(X) - predicts the target variable
    """
    def __init__(self, additional_estimators=None):
        super().__init__(
            "neg_root_mean_squared_error",
            [
                DecisionTreeWrapper(),
                RandomForestWrapper(),
                LinearRegressionWrapper(),
                LassoWrapper(),
                ElasticNetWrapper(),
                RidgeWrapper(),
                LassoLarsICWrapper()
            ],
            DummyRegressor(strategy='mean'),
            'mean',
            additional_estimators
        )
    def get_metric(self):
        return self.metric_

    def get_estimators(self):
        return self.estimators_

    @staticmethod
    def measure_importances(X, y):
        X = X.copy()
        X["really_random_variable"] = np.random.rand(X.shape[0])
        feature_names = X.columns
        forest = RandomForestRegressor()
        forest.fit(X, y)
        importances = forest.feature_importances_
        return pd.Series(importances, index=feature_names)

class DecisionTreeWrapper(EstimatorWrapper):
    def __init__(self):
        param_distributions = {
            "max_depth": randint(1, 31),
            "min_samples_split": randint(2, 61),
            "criterion": ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
            "min_samples_leaf": randint(1, 61),
        }
        super().__init__(DecisionTreeRegressor(), param_distributions, "DecisionTreeRegressor",5) #100)

class RandomForestWrapper(EstimatorWrapper):
    def __init__(self):
        param_distributions = {
            "n_estimators": randint(100, 501),      
            "min_samples_leaf": randint(1, 251),    
            "max_samples": uniform(0.5, 0.5),        
            "max_features": uniform(1e-6, 1 - 1e-6),
        }
        super().__init__(RandomForestRegressor(), param_distributions, "RandomForestRegressor",5) #50)

class LinearRegressionWrapper(EstimatorWrapper):
    def __init__(self):
        param_distributions = {
            "fit_intercept": [True, False],
            "copy_X": [True]
        }
        super().__init__(LinearRegression(), param_distributions, "LinearRegression", None) # None means GridSearchCV

class LassoWrapper(EstimatorWrapper):
    def __init__(self):
        param_distributions = {
            "alpha": uniform(1e-8, 100),
            "fit_intercept": [True, False],
            "copy_X": [True]
        }
        super().__init__(Lasso(), param_distributions, "Lasso", 5)#100)

class RidgeWrapper(EstimatorWrapper):
    def __init__(self):
        param_distributions = {
            "alpha": uniform(1e-8, 100),
            "fit_intercept": [True, False],
            "copy_X": [True]
        }
        super().__init__(Ridge(), param_distributions, "Ridge", 5) #100)

class LassoLarsWrapper(EstimatorWrapper): #depracted
    def __init__(self):
        param_distributions = {
            "alpha": uniform(1e-8, 100),
            "fit_intercept": [True, False],
            "copy_X": [True]
        }
        super().__init__(LassoLars(), param_distributions, "LassoLars", 5) #100)

class LassoLarsICWrapper(EstimatorWrapper):
    def __init__(self):
        param_distributions = {
            "criterion": ['aic', 'bic'],
            "fit_intercept": [True, False],
            "copy_X": [True]
        }
        super().__init__(LassoLarsIC(), param_distributions, "LassoLarsIC", None)

class ElasticNetWrapper(EstimatorWrapper):
    def __init__(self):
        param_distributions = {
            "alpha": uniform(1e-8, 100),
            "l1_ratio": uniform(0.1, 0.9),
            "fit_intercept": [True, False],
            "copy_X": [True]
        }
        super().__init__(ElasticNet(), param_distributions, "ElasticNet", 5) #100)
