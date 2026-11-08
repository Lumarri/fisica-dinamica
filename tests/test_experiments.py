import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from experiments import ExperimentConfig, run_experiment
from models import SolverSettings, harmonic_ensemble, oscillator, wilson_interval


class NumericalResearchTests(unittest.TestCase):
    def test_general_harmonic_analytic_reference(self):
        mass, k, x0, v0 = 2.3, 7.2, -.4, 1.3
        t, y = oscillator(mass=mass, stiffness=k, damping=0, initial=(x0, v0),
                          duration=8, rtol=1e-10, atol=1e-12)
        w = np.sqrt(k/mass)
        np.testing.assert_allclose(y[:, 0], x0*np.cos(w*t)+v0/w*np.sin(w*t), atol=1e-9)
        np.testing.assert_allclose(y[:, 1], -x0*w*np.sin(w*t)+v0*np.cos(w*t), atol=1e-9)

    def test_ensemble_each_realization_conserves_energy(self):
        d = harmonic_ensemble(count=400, mass=2.5, x0=.7, xstd=.2, v0=.3)
        initial_energy = .5*2.5*.3**2+.5*d['stiffness']*d['initial']**2
        terminal_energy = .5*2.5*d['v_terminal']**2+.5*d['stiffness']*d['terminal']**2
        np.testing.assert_allclose(terminal_energy, initial_energy, rtol=1e-12)
        self.assertAlmostEqual(d['probability'], np.mean(d['terminal'] > .5))

    def test_wilson_handles_zero_and_all_successes(self):
        low, high = wilson_interval(0, 100)
        self.assertAlmostEqual(low, 0.)
        self.assertGreater(high, .03)
        low, high = wilson_interval(100, 100)
        self.assertLess(low, .97)
        self.assertAlmostEqual(high, 1.)
        with self.assertRaises(ValueError):
            wilson_interval(1, 0)

    def test_config_roundtrip_preserves_parameters_seed_notes_and_tolerances(self):
        c = ExperimentConfig(model='ensemble', seed=728, notes='Hipótesis: energía conservada',
                             solver=SolverSettings(rtol=2e-9, atol=3e-11, points=400))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'investigacion.json'
            c.save(path)
            loaded = ExperimentConfig.load(path)
        self.assertEqual(loaded, c)
        original = run_experiment(c)
        restored = run_experiment(loaded)
        np.testing.assert_array_equal(original.extra['terminal'], restored.extra['terminal'])

    def test_invalid_projects_and_nonfinite_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            ExperimentConfig.from_dict({'format_version': 99})
        data = ExperimentConfig().to_dict()
        data['model'] = 'unknown'
        with self.assertRaises(ValueError):
            ExperimentConfig.from_dict(data)
        for config in [ExperimentConfig(mass=float('nan')),
                       ExperimentConfig(duration=float('inf')),
                       ExperimentConfig(model='ensemble', stiffness=1, stiffness_std=1),
                       ExperimentConfig(solver=SolverSettings(atol=0))]:
            with self.subTest(config=config), self.assertRaises(ValueError):
                config.validate()

    def test_refinement_diagnostic_and_csv_include_same_computed_states(self):
        c = ExperimentConfig(duration=2, damping=0, solver=SolverSettings(points=200))
        result = run_experiment(c)
        self.assertLess(result.extra['analytic_error'], 1e-7)
        self.assertLess(result.extra['scaled_difference'], 1e-7)
        np.testing.assert_allclose(result.dataframe()['x_m'], result.states[:, 0])
        self.assertIn('diferencia_refinada_x_m', result.dataframe())
        # El resultado no cambia si el formulario original se modifica.
        c.mass = 5.
        self.assertEqual(result.config.mass, 1.)

    def test_lorenz_initial_perturbation_and_finite_states(self):
        c = ExperimentConfig(model='lorenz', duration=2, delta=.002,
                             solver=SolverSettings(points=200))
        r = run_experiment(c)
        self.assertAlmostEqual(r.extra['separation'][0], c.delta)
        self.assertTrue(np.isfinite(r.states).all())
        self.assertTrue(np.isfinite(r.refined).all())


if __name__ == '__main__':
    unittest.main()
