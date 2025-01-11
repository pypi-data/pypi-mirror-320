import numpy as np
import sympy as sp
from scipy.optimize import fsolve
import mpmath
t, s = sp.symbols('t s')

def samplified(V):
    return(sp.simplify(v))

# Cache the lambdified function
@lru_cache(maxsize=None)
def function(F):
    return sp.lambdify(s, F, 'mpmath')

# Optimized inverse Laplace transform function
def inverse_laplace(F, t_val):
    if t_val <= 0:
        return 0 
    F_func = get_lambdified_func(F)
    return float(mpmath.invertlaplace(F_func, t_val, method='talbot'))

__all__ = ['inverse_laplace', 'function', 'samplified']
