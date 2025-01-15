import optax

from jax import value_and_grad, jit
from typing import Tuple, Dict, Callable
from functools import partial
from jaxtyping import Key, Array, Float, Int, Bool
#model: GP
def train(
        model: Callable, 
        key: Key, 
        number_iterations: Int =1000, 
        number_restarts: int=1, 
        lr: float=1e-2, 
        save_history: Bool=False, 
        verbose: Bool=True
    ) -> Tuple:
    kernel = model.kernel
    likelihood = model.likelihood
    nlml = partial(likelihood, model.X, model.Y, model.sigma_sq, model.jitter)

    def loss_fn(params: Dict) -> float:
        kernel.update_params(params)
        return nlml(kernel)

    value_and_grad_fn = value_and_grad(loss_fn)

    opt = optax.adam(lr)
    
    @jit
    def step(params: Dict, opt_state: Dict) -> Tuple:
        loss, grads = value_and_grad_fn(params)
        updates, opt_state = opt.update(grads, opt_state)
        params = optax.apply_updates(params, updates)
        return params, opt_state, loss
    
    def loop(params: Dict, opt_state: Dict) -> Tuple:
        for _ in range(number_iterations):
            params, opt_state, loss = step(params, opt_state)
        return params, opt_state, loss
    
    #make several restarts with different initializations
    dict_params = {}
    for _ in range(number_restarts):
        params = kernel.sample_hyperparameters(key)
        opt_state = opt.init(params)
        params, opt_state, loss = loop(params, opt_state)
        dict_optimization_run = {"params": params, "loss": loss, "key": key}
        dict_params["run_{}".format(_)] = dict_optimization_run
        if verbose:
            print(f"Loss: {loss}")

    best_run = min(dict_params, key=lambda x: dict_params[x]['loss'])
    print("best run: ",best_run, ":", dict_params[best_run]['loss'])
    if save_history:
        print("All optimization runs saved.")
        return dict_params[best_run], dict_params
    return dict_params[best_run], None
    