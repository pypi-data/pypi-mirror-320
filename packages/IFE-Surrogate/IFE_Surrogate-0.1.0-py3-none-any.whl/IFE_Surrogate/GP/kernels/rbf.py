from dataclasses import dataclass
from jaxtyping import Array
from typing import Callable, Dict
import jax.numpy as jnp

from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel



@dataclass
class RBF(AbstractKernel):
    lengthscale: Array
    variance: float
    priors: Dict[str, Callable]=None

    def evaluate(self, x1: Array, x2: Array) -> Array:
        sq_dist = jnp.sum(jnp.abs(x1[:, None] - x2)**2 * self.lengthscale**-2, axis=-1)
        return self.variance * jnp.exp(-0.5 * sq_dist)

    






