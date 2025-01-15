from jaxtyping import Array
from typing import Tuple
import jax.numpy as jnp
from jax import scipy as jsp

def predictive_mean_var_wideband(
        X_train: Array, 
        Y_train: Array,
        sigma_sq: float,
        kernel ,
        jitter: float,
        X_test: Array,
    ) -> Tuple[Array, Array]:
    """
    Calculates the posterior distribution mean and variance for a diagonal covariance matrix.

    Args:
        X (ndarray): The training input data., shape (N, D).
        Y_train (ndarray): The training output data. shape (N,P).
        X_test (ndarray): The test input data. shape (M, D).
        params (dict): The parameters for the kernel function. 
        jitter (float): The jitter value to add to the diagonal of the covariance matrix.
        sigma_sq (float): The variance of the noise.

    Returns:
        tuple: A tuple containing the mean and variance of the posterior distribution. Both have shape (M, P).
    """
    N = X_train.shape[0]
    K = kernel(X_train, X_train) * sigma_sq
    L = jsp.linalg.cho_factor(K + jitter*jnp.eye(N), lower=True)
    alpha = jsp.linalg.cho_solve(L, Y_train)
    k_star = kernel(X_train, X_test) * sigma_sq
    f_star = jnp.dot(k_star.T, alpha)
    v = jnp.linalg.solve(L[0], k_star)
    var_f_star = kernel(X_test, X_test) * sigma_sq - jnp.dot(v.T, v)
    var_f_star = jnp.diag(var_f_star)
    return f_star, var_f_star
