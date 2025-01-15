from typing import Callable
import jax.numpy as jnp
import jax.scipy as jsp
from jax import vmap
from jaxtyping import Array, Float


def nmll_wideband(
        X: Array,
        Y: Array,
        sigma_sq: Array,
        jitter: Float,
        kernel: Callable,
    ) -> Float:
    """
    Calculate the negative marginal log-likelihood (NMLL) for a wideband Gaussian Process model.
        - X: Array
            The input data matrix.
        - Y: Array
            The output data matrix.
        - sigma_sq: Array
            The variance of the noise.
        - jitter: Float
            A small value added to the diagonal of the kernel matrix for numerical stability.
        - kernel: Callable
            The kernel function used to compute the covariance matrix.
        - nmll: Float
            The negative marginal log-likelihood value.
    """
    def calc_inner_loops(Y_minus_mean, L):
        """
        Calculate the inner loops of a function.

        Parameters:
        - Y_minus_mean: The difference between Y and the mean value.
        - L: The matrix L.

        Returns:
        - The result of the calculation.
            """
        return 0.5 * jnp.dot((Y_minus_mean).T, jsp.linalg.cho_solve((L, True), Y_minus_mean))
    
    inner_loop = vmap(calc_inner_loops, in_axes=(1, None))
    
    p_ = Y.shape[1]
    N = Y.shape[0]
    K = kernel(X, X)
    L = jsp.linalg.cho_factor(K + jitter*jnp.eye(N), lower=True)[0]
    
    nmll = (N*p_/2 * jnp.log(2*jnp.pi) 
            +  p_ * jnp.log(jnp.sum(jnp.diag(L))) 
            + N/2 * jnp.sum(jnp.log(sigma_sq))) 
    
    nmll += jnp.sum(inner_loop(Y, L) * sigma_sq**-1)
            
    return nmll
