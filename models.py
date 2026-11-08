"""Modelos reproducibles. Unidades SI para el oscilador."""
import numpy as np
from scipy.integrate import solve_ivp


def integrate(model, initial, duration=30., points=2000):
    if duration <= 0 or points < 2:
        raise ValueError("Duración y número de puntos inválidos")
    t = np.linspace(0, duration, points)
    result = solve_ivp(model, (0, duration), initial, t_eval=t,
                       rtol=1e-8, atol=1e-10)
    if not result.success or not np.isfinite(result.y).all():
        raise ValueError("La integración no convergió")
    return result.t, result.y.T


def oscillator(mass=1., stiffness=4., damping=.2, initial=(1., 0.), duration=30.):
    if mass <= 0 or stiffness <= 0 or damping < 0:
        raise ValueError("m y k deben ser positivos; c no negativo")
    return integrate(lambda t, y: [y[1], -(stiffness*y[0]+damping*y[1])/mass],
                     initial, duration)


def lorenz(sigma=10., rho=28., beta=8/3, initial=(1., 1., 1.), duration=30.):
    def rhs(t, y):
        x, v, z = y
        return [sigma*(v-x), x*(rho-z)-v, x*v-beta*z]
    return integrate(rhs, initial, duration, 4000)


def monte_carlo(count=1000, seed=42, mean=4., std=.4, duration=10., threshold=.5):
    """Incertidumbre uniforme de k, con media y desviación indicadas.

    Oscilador sin amortiguamiento, m=1 kg, x(0)=1 m, v(0)=0.
    """
    if count < 2 or std < 0 or mean-3**.5*std <= 0 or duration <= 0:
        raise ValueError("La distribución de rigidez debe ser positiva")
    rng = np.random.default_rng(seed)
    k = rng.uniform(mean-3**.5*std, mean+3**.5*std, count)
    t = np.linspace(0, duration, 400)
    trajectories = np.cos(np.sqrt(k[:, None])*t)
    terminal = trajectories[:, -1]
    probability = np.mean(terminal > threshold)
    se = np.sqrt(probability*(1-probability)/count)
    return t, trajectories, terminal, float(probability), float(se)
