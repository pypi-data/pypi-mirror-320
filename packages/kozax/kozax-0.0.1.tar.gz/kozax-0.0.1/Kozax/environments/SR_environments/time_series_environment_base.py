"""
Kozax: Genetic programming framework in JAX

Copyright (c) 2024 sdevries0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import jax
import jax.numpy as jnp
import jax.random as jrandom
import abc

_itemsize_kind_type = {
    (1, "i"): jnp.int8,
    (2, "i"): jnp.int16,
    (4, "i"): jnp.int32,
    (8, "i"): jnp.int64,
    (2, "f"): jnp.float16,
    (4, "f"): jnp.float32,
    (8, "f"): jnp.float64,
}

def force_bitcast_convert_type(val, new_type=jnp.int32):
    val = jnp.asarray(val)
    intermediate_type = _itemsize_kind_type[new_type.dtype.itemsize, val.dtype.kind]
    val = val.astype(intermediate_type)
    return jax.lax.bitcast_convert_type(val, new_type)

class EnvironmentBase(abc.ABC):
    def __init__(self, process_noise, obs_noise, n_var, n_obs):
        self.process_noise = process_noise
        self.obs_noise = obs_noise
        self.n_var = n_var
        self.n_obs = n_obs

    @abc.abstractmethod
    def sample_init_states(self, batch_size, key):
        return

    def f_obs(self, key, t_x):
        t, x = t_x
        new_key = jrandom.fold_in(key, force_bitcast_convert_type(t))
        out = self.C@x + jrandom.normal(new_key, shape=(self.n_obs,))@self.W
        return key, out
    
    @abc.abstractmethod
    def drift(self, t, state, args):
        return

    @abc.abstractmethod
    def diffusion(self, t, state, args):
        return

    def terminate_event(self, state, **kwargs):
        return False