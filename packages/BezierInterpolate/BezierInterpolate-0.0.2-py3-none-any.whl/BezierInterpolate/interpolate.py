import numpy as np
import pandas as pd
from collections.abc import Callable
from pandas.api.types import is_numeric_dtype

def memoize(f:Callable):
    cache = {}
    def wrapper(t:int):
        if t not in cache:
            cache[t] = f(t)
        return cache[t]
    return wrapper

@memoize
def factorial(n:int):
    if n < 0:
        raise ValueError('n need to be non-negative integer')
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)
    

def binomial_coefficient(n:int,k:int)->float:
    return factorial(n)/(factorial(k) * factorial(n-k))

def bernstein_polynomial(index:int,degree:int,t:float):
    return binomial_coefficient(degree,index) * t**index * (1-t)**(degree-index)

def bezier_curve(control_points:np.ndarray,degree:int,t:np.ndarray):
    return np.array([
        sum(
            control_points[i] * bernstein_polynomial(i,degree,t[j]) for i in range(degree+1)
        ) 
        for j in range(len(t))
    ])

def bezier_gradient(degree:int,t:np.ndarray):
    return np.array(
        [
            [
                bernstein_polynomial(i,degree,t[j])
                for i in range(degree+1)
            ]
            for j in range(len(t))
        ]
    ).T


def least_square_fit(data:np.ndarray,t:np.ndarray,degree:int):
    A = bezier_gradient(degree,t)
    control_points = np.linalg.pinv(A@A.T) @ (A @ data)
    return control_points


def bezier(data:pd.DataFrame | pd.Series, degree:int):

    if not isinstance(data,pd.Series) and not isinstance(data,pd.DataFrame):
        raise Exception('Data should be either Pandas Series or Pandas DataFrame')
    
    if not isinstance(degree, int) and degree < 0:
        raise ValueError('Degree must be non-negative integer')
    
    if len(data.shape) > 1 and data.shape[1] > 1:
        raise Exception('Does not support multivariate data')
    
    if not is_numeric_dtype(data.values):
        raise ValueError('Data must have numeric dtype')
    
    if data.isna().sum().sum() == 0:
        return data
    
    t = np.linspace(0,1,len(data))

    if isinstance(data,pd.DataFrame):
        nan_mask = data.isna().values.reshape(len(data),)
        filled = data[~nan_mask].values.reshape(len(data[~nan_mask],))
    else:
        nan_mask = data.isna().values
        filled = data[~nan_mask].values
    
    
    control_points = least_square_fit(filled,t[~nan_mask],degree)

    if isinstance(data,pd.DataFrame):
        res = pd.DataFrame(bezier_curve(control_points,degree,t),index=data.index,columns=data.columns)
    else:
        res = pd.Series(bezier_curve(control_points,degree,t),index=data.index,name=data.name)

    data = data.fillna(res)

    return data