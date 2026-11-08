"""Configuración, resultados y persistencia reproducible del laboratorio."""
from dataclasses import asdict, dataclass, field, fields
import json
from pathlib import Path

import numpy as np
import pandas as pd

from models import SolverSettings, harmonic_ensemble, lorenz, oscillator
from catalog import MODELS, MODEL_NAMES, EXAMPLES


@dataclass
class ExperimentConfig:
    model: str = "oscillator"
    duration: float = 25.
    mass: float = 1.
    stiffness: float = 4.
    damping: float = .2
    x0: float = 1.
    v0: float = 0.
    sigma: float = 10.
    rho: float = 28.
    beta: float = 8/3
    y0: float = 1.
    z0: float = 1.
    delta: float = .0001
    count: int = 1000
    seed: int = 42
    stiffness_std: float = .4
    position_std: float = .05
    threshold: float = .5
    project_name: str = 'Experimento sin título'
    researcher: str = ''
    objective: str = ''
    references: str = ''
    parameters: dict = field(default_factory=dict)
    notes: str = ""
    solver: SolverSettings = field(default_factory=SolverSettings)

    def validate(self):
        if self.model not in MODEL_NAMES:
            raise ValueError("Modelo no reconocido.")
        numeric = [getattr(self, f.name) for f in fields(self)
                   if f.name not in {"model", "notes", "solver", "parameters", "project_name", "researcher", "objective", "references"}]
        try:
            valid = np.isfinite(np.asarray(numeric, dtype=float)).all()
        except (TypeError, ValueError):
            valid = False
        if not valid:
            raise ValueError("Los parámetros deben ser números finitos.")
        spec = MODELS[self.model]
        if spec.timed and not spec.time_range[0] <= self.duration <= spec.time_range[1]:
            raise ValueError(f"Duración fuera de rango: {spec.time_range[0]:g} a {spec.time_range[1]:g} {spec.time_unit}.")
        if not .05 <= self.mass <= 100 or not .05 <= self.stiffness <= 100 or not 0 <= self.damping <= 30:
            raise ValueError("Masa, rigidez o amortiguamiento fuera de rango.")
        if any(not -100 <= x <= 100 for x in [self.x0, self.v0, self.y0, self.z0]):
            raise ValueError("Las condiciones iniciales deben estar entre -100 y 100.")
        if not .1 <= self.sigma <= 50 or not 0 <= self.rho <= 100 or not .1 <= self.beta <= 10:
            raise ValueError("Parámetros de Lorenz fuera de rango.")
        if not 1e-8 <= self.delta <= 1 or not 0 <= self.stiffness_std <= 10 or not 0 <= self.position_std <= 10:
            raise ValueError("Perturbación o dispersiones fuera de rango.")
        if not isinstance(self.count, int) or not 100 <= self.count <= 10000:
            raise ValueError("Usa entre 100 y 10000 realizaciones.")
        if not isinstance(self.seed, int) or not 0 <= self.seed <= 2147483647:
            raise ValueError("Semilla inválida.")
        if not -100 <= self.threshold <= 100 or not isinstance(self.notes, str) or len(self.notes) > 100000:
            raise ValueError("Umbral o notas inválidos.")
        if self.model == "ensemble" and self.stiffness-np.sqrt(3)*self.stiffness_std <= 0:
            raise ValueError("Reduce la desviación de rigidez: K debe ser siempre positiva.")
        self.solver.validate()
        for key in ['project_name', 'researcher', 'objective', 'references']:
            if not isinstance(getattr(self, key), str) or len(getattr(self, key)) > 10000:
                raise ValueError('Los datos del proyecto deben ser texto de hasta 10000 caracteres.')
        parameters = spec.values(self.parameters)
        if self.model not in {'oscillator','lorenz','ensemble'}:
            from advanced_models import validate_model
            validate_model(self.model, parameters, self)
        self.parameters = parameters

    def to_dict(self):
        self.validate()
        return {"format_version": 2, **asdict(self)}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict) or data.get("format_version") not in {1, 2}:
            raise ValueError("Formato de proyecto no compatible (se espera versión 1 o 2).")
        values = dict(data)
        values.pop("format_version")
        try:
            values["solver"] = SolverSettings(**values.get("solver", {}))
            config = cls(**values)
            config.validate()
        except (TypeError, AttributeError) as error:
            raise ValueError("Estructura de configuración inválida.") from error
        return config

    def save(self, path):
        Path(path).write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2,
                                        allow_nan=False), encoding="utf-8")

    @classmethod
    def load(cls, path):
        path = Path(path)
        if path.stat().st_size > 1024*1024:
            raise ValueError("El archivo de proyecto supera 1 MB.")
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


@dataclass
class ExperimentResult:
    config: ExperimentConfig
    t: np.ndarray
    states: np.ndarray
    refined: np.ndarray | None = None
    extra: dict = field(default_factory=dict)

    def dataframe(self):
        if 'data' in self.extra:
            return self.extra['data']
        if self.config.model == "ensemble":
            e = self.extra
            return pd.DataFrame({"realizacion": np.arange(1, self.config.count+1),
                                 "rigidez_N_m": e["stiffness"], "x0_m": e["initial"],
                                 "posicion_final_m": e["terminal"],
                                 "velocidad_final_m_s": e["v_terminal"]})
        names = ["x_m", "v_m_s"] if self.config.model == "oscillator" else ["x", "y", "z"]
        frame = pd.DataFrame(self.states, columns=names)
        frame.insert(0, "t_s" if self.config.model == "oscillator" else "t_adimensional", self.t)
        if self.config.model == "oscillator":
            frame["energia_J"] = self.extra["energy"]
        else:
            frame["separacion"] = self.extra["separation"]
        if self.refined is not None:
            for i, name in enumerate(names):
                frame["diferencia_refinada_"+name] = np.abs(self.states[:, i]-self.refined[:, i])
        return frame


def run_experiment(config):
    config.validate()
    # Copia: el resultado siempre describe los parámetros que lo produjeron.
    config = ExperimentConfig.from_dict(config.to_dict())
    if config.model not in {'oscillator','lorenz','ensemble'}:
        from advanced_models import run_advanced
        return ExperimentResult(config=config, **run_advanced(config))
    if config.model == "ensemble":
        config.damping = 0.
        e = harmonic_ensemble(count=config.count, seed=config.seed,
            mean=config.stiffness, std=config.stiffness_std, mass=config.mass,
            x0=config.x0, xstd=config.position_std, v0=config.v0,
            duration=config.duration, threshold=config.threshold, points=config.solver.points)
        omega = np.sqrt(config.stiffness/config.mass)
        t = e["t"]
        x = config.x0*np.cos(omega*t)+config.v0/omega*np.sin(omega*t)
        v = -config.x0*omega*np.sin(omega*t)+config.v0*np.cos(omega*t)
        e["quantiles"] = np.quantile(e["paths"], [.025, .5, .975], axis=0)
        return ExperimentResult(config, t, np.column_stack([x, v]), extra=e)

    normal = config.solver.kwargs()
    refined = dict(normal, rtol=max(1e-13, config.solver.rtol/10),
                   atol=max(1e-15, config.solver.atol/10), max_step=config.solver.max_step/2)
    if config.model == "oscillator":
        args = dict(mass=config.mass, stiffness=config.stiffness, damping=config.damping,
                    initial=(config.x0, config.v0), duration=config.duration)
        t, states = oscillator(**args, **normal)
        _, reference = oscillator(**args, **refined)
        extra = {"energy": .5*config.mass*states[:, 1]**2+.5*config.stiffness*states[:, 0]**2}
        if config.damping == 0:
            omega = np.sqrt(config.stiffness/config.mass)
            exact = config.x0*np.cos(omega*t)+config.v0/omega*np.sin(omega*t)
            extra["analytic_error"] = float(np.max(np.abs(states[:, 0]-exact)))
    else:
        args = dict(sigma=config.sigma, rho=config.rho, beta=config.beta,
                    initial=(config.x0, config.y0, config.z0), duration=config.duration)
        t, states = lorenz(**args, **normal)
        _, reference = lorenz(**args, **refined)
        args["initial"] = (config.x0+config.delta, config.y0, config.z0)
        _, perturbed = lorenz(**args, **normal)
        extra = {"separation": np.linalg.norm(states-perturbed, axis=1), "perturbed": perturbed}
    extra["absolute_difference"] = np.max(np.abs(states-reference), axis=0)
    scale = np.maximum(1., np.max(np.abs(reference), axis=0))
    extra["scaled_difference"] = float(np.max(np.abs(states-reference)/scale))
    return ExperimentResult(config, t, states, reference, extra)


def example_config(key):
    example = next((example for example in EXAMPLES if example.key == key), None)
    if example is None:
        raise ValueError('Ejemplo no reconocido.')
    values = dict(model=example.model, duration=MODELS[example.model].duration,
                  project_name=example.label, objective=example.expected,
                  references='; '.join(label+': '+url for label,url in MODELS[example.model].references),
                  parameters=dict(example.parameters), notes='Resultado esperado:\n'+example.expected)
    values.update(example.values)
    config = ExperimentConfig(**values)
    config.validate()
    return config
