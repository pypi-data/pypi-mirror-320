from IFE_Surrogate.GP.abstract_gp import AbstractGP
from IFE_Surrogate.GP.train import train
from IFE_Surrogate.GP.likelihood import nmll_wideband
from IFE_Surrogate.GP.inference import predictive_mean_var_wideband
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel

from jaxtyping import Key, Array, Int, Bool
from typing import Tuple
from functools import partial
from jax import vmap
import typing
from jax import numpy as jnp
import numpyro
from numpyro import distributions as dist
from numpyro.infer import MCMC, NUTS

Kernel = typing.TypeVar("Kernel", bound=AbstractKernel)

class wideband_GP(AbstractGP):
    """
    Wideband Gaussian Process for multi-output regression.

    Parameters
    ----------
    X : Array
        Training input data
    Y : Array
        Training output data
    kernel : Kernel
        Kernel object to be used in the GP model
    """
    def __init__(self, X: Array, Y: Array, kernel: Kernel):
        assert X.shape[0] == Y.shape[0] , "X and Y should have the same number of samples"
        assert Y.shape[1] > 1, "Y should be a matrix with shape (N, p) N: #samples, p: #outputs"
        super().__init__(kernel, X, Y)
        self.likelihood = nmll_wideband
        self.sigma_sq = Y.var(axis=0)
        self.jitter = 1e-6

    def train(
        self, 
        key: Key, 
        num_steps: Int =1000, 
        number_restarts: int=1, 
        lr: float=1e-2, 
        save_history: Bool=False, 
        verbose: Bool=False
    ) -> Tuple:
        
        self.optimized_parameters, self.parameter_history = train(
            self, key, num_steps, number_restarts, lr, save_history, verbose
        )
        self.kernel.update_params(self.optimized_parameters["params"])

        pass

    def predict(self, X_test: Array) -> Tuple[Array, Array]:
        pred_wideband = partial(predictive_mean_var_wideband, self.X, kernel=self.kernel, jitter=self.jitter, X_test=X_test)
        mean, var = vmap(pred_wideband, in_axes=(1,0))(self.Y, self.sigma_sq)
        return mean, var
   
    def sample_posterior(self, key: Key, X: Array, n_samples: Int) -> Array:
        pass
    def sample_prior(self, key: Key, X: Array, n_samples: Int) -> Array:
        pass
    def save(self, path: str):
        pass


class wideband_gp_baysian(AbstractGP):
    def __init__(self, kernel, X, Y):
        super().__init__(kernel, X, Y)
        self.likelihood = nmll_wideband
        self.sigma_sq = Y.var(axis=0)
        self.jitter = 1e-6
    
    def model_forward(self,):
        n,p = self.X.shape[0], self.Y.shape[1]  
        variance = 1.#numpyro.sample("variance", self.kernel.priors["variance"])
        lengthscale = numpyro.sample("lengthscale", self.kernel.priors["lengthscale"])

        self.kernel.update_params({"variance": variance, "lengthscale": lengthscale})
        K = self.kernel(self.X, self.X) + jnp.eye(n) * 1e-4
        
        normal = dist.MultivariateNormal(jnp.zeros(n), K)
        #here again we make the assumption that we dont need to use the variance as a hyperparameter,
        #but just use the data variance
        data_variances = jnp.var(self.Y, axis=0)

        with numpyro.plate("frequency_positions", p): #plate 
            #here I use a little trick so we do not have to calculate the normal distribution for each task
            # N(0, sigma^2) = N(0, 1) / sigma
            obs = self.Y/jnp.sqrt(data_variances)
            for i in range(p):
                numpyro.sample(
                    f"Y{i}", 
                    normal, 
                    obs=obs[:, i], 
                )


    def train(self, key: Key, num_samples:Int = 100, num_warmup:Int = 100):
        nuts_kernel = NUTS(self.model_forward)
        mcmc = MCMC(nuts_kernel, num_warmup=num_warmup, num_samples=num_samples)
        mcmc.run(key, )
        mcmc.print_summary()
        samples = mcmc.get_samples()
        self.samples = samples
    def predict(self, X_test: Array):
        pred_one_sample = partial(predictive_mean_var_wideband, self.X, kernel=self.kernel, jitter=self.jitter, X_test=X_test)
        vmap_over_frequency = vmap(pred_one_sample, in_axes=(1,0))
        
        
        
    def sample_posterior():
        pass
    def sample_prior():
        pass
    def save():
        pass

