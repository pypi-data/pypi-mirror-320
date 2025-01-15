""" 
"""
from jaxtyping import Array
from abc import ABC, abstractmethod
import typing
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel
Kernel = typing.TypeVar("Kernel", bound=AbstractKernel)


class AbstractGP(ABC):
    """ 
        Abstract base class of a GP, to be used as skeleton for actual GP implementations.
    """
    def __init__(self, kernel: Kernel, X: Array, Y: Array):
        self.kernel = kernel
        self.X = X
        self.Y = Y

    @abstractmethod
    def train():
        return

    @abstractmethod
    def predict():
        return

    @abstractmethod
    def sample_prior():
        return

    @abstractmethod
    def sample_posterior():
        return

    @abstractmethod
    def save():
        return

