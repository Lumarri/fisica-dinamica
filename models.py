"""Modelos físicos e integración numérica independientes de la interfaz."""
from dataclasses import dataclass
from numbers import Integral

import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class SolverSettings:
    rtol: float = 1e-9
    atol: float = 1e-11
    max_step: float = 0.05
    points: int = 1200

    def validate(self):
        if not (1e-12 <= self.rtol <= 1e-3):
            raise ValueError("La tolerancia relativa debe estar entre 1e-12 y 1e-3.")
        if not (1e-14 <= self.atol <= 1e-3):
            raise ValueError("La tolerancia absoluta debe estar entre 1e-14 y 1e-3.")
        if not np.isfinite(self.max_step) or not 0.001 <= self.max_step <= 2:
            raise ValueError("El paso máximo debe estar entre 0.001 y 2.")
        if not isinstance(self.points, Integral) or not 200 <= self.points <= 3000:
            raise ValueError("El muestreo temporal debe tener entre 200 y 3000 puntos.")

    def kwargs(self):
        self.validate()
        return dict(rtol=self.rtol, atol=self.atol, max_step=self.max_step,
                    points=self.points, method="DOP853")

def _finite(*values):
    try:
        valid = np.isfinite(np.asarray(values, dtype=float)).all()
    except (TypeError, ValueError):
        valid = False
    if not valid:
        raise ValueError("Todos los parámetros deben ser números finitos.")


def integrate(model, initial, duration=30., points=2000, *, rtol=1e-9,
              atol=1e-11, max_step=0.05, method="DOP853"):
    _finite(duration, rtol, atol, max_step)
    _finite(*initial)
    if not 0 < duration <= 120 or not isinstance(points, Integral) or not 2 <= points <= 10000:
        raise ValueError("Duración (0, 120] o número de puntos inválidos.")
    if rtol <= 0 or atol <= 0 or max_step <= 0:
        raise ValueError("Las tolerancias y el paso deben ser positivos.")
    t = np.linspace(0, duration, points)
    result = solve_ivp(model, (0, duration), initial, t_eval=t, method=method,
                       rtol=rtol, atol=atol, max_step=max_step)
    if not result.success or result.y.shape[1] != points or not np.isfinite(result.y).all():
        raise ValueError("La integración no convergió. Revisa los parámetros.")
    return result.t, result.y.T


def oscillator(mass=1., stiffness=4., damping=.2, initial=(1., 0.),
               duration=30., **solver):
    _finite(mass, stiffness, damping)
    if mass <= 0 or stiffness <= 0 or damping < 0 or len(initial) != 2:
        raise ValueError("m y k deben ser positivos; c no negativo; estado inicial (x, v).")
    return integrate(lambda t, y: [y[1], -(stiffness*y[0]+damping*y[1])/mass],
                     initial, duration, **solver)


def lorenz(sigma=10., rho=28., beta=8/3, initial=(1., 1., 1.),
           duration=30., **solver):
    _finite(sigma, rho, beta)
    if sigma <= 0 or rho < 0 or beta <= 0 or len(initial) != 3:
        raise ValueError("σ y β deben ser positivos; ρ no negativo; estado inicial (x, y, z).")

    def rhs(t, y):
        x, v, z = y
        return [sigma*(v-x), x*(rho-z)-v, x*v-beta*z]
    return integrate(rhs, initial, duration, **solver)


def wilson_interval(successes, count, z=1.959963984540054):
    """Intervalo de Wilson bilateral del 95 % para una probabilidad binomial."""
    if not isinstance(count, Integral) or count < 1 or not 0 <= successes <= count:
        raise ValueError("Recuento binomial inválido.")
    p = successes / count
    scale = 1 + z*z/count
    center = (p + z*z/(2*count)) / scale
    half = z*np.sqrt(p*(1-p)/count + z*z/(4*count*count)) / scale
    return max(0., center-half), min(1., center+half)


def harmonic_ensemble(count=1000, seed=42, mean=4., std=.4, mass=1.,
                      x0=1., xstd=.05, v0=0., duration=10., threshold=.5,
                      points=1200):
    """Variables independientes uniformes K y X0; solución analítica exacta.

    Muestreo temporal y aritmética de coma flotante conservan sus limitaciones.
    Las bandas son percentiles del conjunto, no IC de la media.
    """
    _finite(mean, std, mass, x0, xstd, v0, duration, threshold)
    if not isinstance(count, Integral) or not 2 <= count <= 10000:
        raise ValueError("Usa entre 2 y 10000 realizaciones.")
    if not isinstance(seed, Integral) or not 0 <= seed <= 2147483647:
        raise ValueError("La semilla debe ser un entero entre 0 y 2147483647.")
    if (mass <= 0 or std < 0 or xstd < 0 or mean-np.sqrt(3)*std <= 0
            or not 0 < duration <= 120 or not isinstance(points, Integral)
            or not 200 <= points <= 3000):
        raise ValueError("La rigidez debe ser positiva; comprueba masa, dispersiones y duración.")
    rng = np.random.default_rng(seed)
    stiffness = rng.uniform(mean-np.sqrt(3)*std, mean+np.sqrt(3)*std, count)
    initial = rng.uniform(x0-np.sqrt(3)*xstd, x0+np.sqrt(3)*xstd, count)
    omega = np.sqrt(stiffness/mass)
    t = np.linspace(0, duration, points)
    phase = omega[:, None]*t
    paths = initial[:, None]*np.cos(phase) + (v0/omega[:, None])*np.sin(phase)
    terminal = paths[:, -1]
    v_terminal = -initial*omega*np.sin(omega*duration)+v0*np.cos(omega*duration)
    successes = int(np.count_nonzero(terminal > threshold))
    probability = successes/count
    return dict(t=t, paths=paths, terminal=terminal, v_terminal=v_terminal,
                stiffness=stiffness, initial=initial, omega=omega,
                probability=probability, interval=wilson_interval(successes, count),
                standard_error=float(np.sqrt(probability*(1-probability)/count)))


def monte_carlo(count=1000, seed=42, mean=4., std=.4, duration=10., threshold=.5):
    """Compatibilidad con los experimentos iniciales: m=1, X0=1, v0=0."""
    data = harmonic_ensemble(count=count, seed=seed, mean=mean, std=std,
                            duration=duration, threshold=threshold, xstd=0., points=400)
    return data['t'], data['paths'], data['terminal'], data['probability'], data['standard_error']
