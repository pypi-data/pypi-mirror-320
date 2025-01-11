import numpy as np
import sympy as sp
from scipy.optimize import fsolve
import mpmath
t, s = sp.symbols('t s')


def inverse_laplace(F, t_val):
    if t_val <= 0:
        return 0 
    F_func = sp.lambdify(s, F, 'mpmath')
    return float(mpmath.invertlaplace(F_func, t_val, method='talbot'))

__all__ = ['inverse_laplace']
