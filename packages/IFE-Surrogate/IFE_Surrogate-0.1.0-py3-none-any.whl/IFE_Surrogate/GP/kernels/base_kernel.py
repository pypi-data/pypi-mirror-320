from abc import ABC, abstractmethod
from typing import Callable, Dict, Tuple
import jax.numpy as jnp
from jax import random as jr
from jaxtyping import Array
import numpyro.handlers as handlers


class AbstractKernel(ABC):
    """
    Abstract base class for kernels in Gaussian Process regression.

    Attributes:
        lengthscale: Lengthscale parameter(s) of the kernel.
        variance: Variance (scale) parameter of the kernel.
        priors: A callable prior function for sampling the lengthscale.
    """

    def __init__(
            self, 
            #priors: Dict[str, Callable], #into docstring dictionary with keys as the parameter names and callables as the prior functions
        ) -> None:
        """
        Initialize the kernel.

        Args:
            lengthscale: Lengthscale parameter(s) of the kernel.
            variance: Variance (scale) parameter of the kernel.
            prior_len: A callable prior function for sampling the lengthscale.
        """
        #assert isinstance(priors, Dict), "priors must be a dictionary"
        #assert 

        #sanity check if prior keys match parameters(attributes) of the class
        pass
    
    @abstractmethod
    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the kernel function.

        Args:
            x1: First input data array.
            x2: Second input data array.

        Returns:
            Kernel evaluation between x1 and x2.
        """
        pass

    def __call__(self, x1: Array, x2: Array) -> Array:
        """
        

        Args:
            x1: First input data array.
            x2: Second input data array.

        Returns:
            Kernel evaluation between x1 and x2.
        """
        return self.evaluate(x1, x2)
    
    def eval_matrix(self, X1: Array, X2: Array) -> Array:
        """
        Evaluate the kernel matrix.

        Args:
            X1: First input data matrix.
            X2: Second input data matrix.

        Returns:
            Kernel matrix between X1 and X2.
        """
        ###vmap
        raise NotImplementedError

    def get_params(self) -> Dict[str, Array]:
        """
        Get the kernel parameters.

        Returns:
            A dictionary containing the kernel parameters.
        """
        return {x: y for x,y in self.__dict__.items() if x != 'priors'}
        

    def sample_hyperparameters(self, key) -> Dict[str, Array]:
        """
        Sample new parameters from the prior distribution.

        Args:
            key: JAX random key.

        Returns:
            A dictionary containing sampled parameters.
        """
        #maybe rewrite this to be more readable
        assert isinstance(key, Array), "key must be a jax random key"
        assert key.shape == (2,), "key must be of shape (2,)"
        if self.priors is None:
            print("No priors specified. Returning current parameters.")
            return self.get_params()
        
        param_samples = {x: self.priors[x].sample(key, self.__dict__[x].shape) for x in self.__dict__ if x != 'priors'}
        return param_samples

    def update_params(self, params: Dict[str, Array]):
        """
        Update the kernel parameters.

        Args:
            params: A dictionary containing the new parameters.
        """
        for key in params:
            self.__dict__[key] = params[key]
