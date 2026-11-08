import unittest
import numpy as np
from models import oscillator, lorenz, monte_carlo

class ModelsTest(unittest.TestCase):
    def test_oscillator_matches_analytic_solution(self):
        t,y = oscillator(damping=0.,duration=10.)
        np.testing.assert_allclose(y[:,0], np.cos(2*t), atol=1e-6)

    def test_damping_dissipates_energy(self):
        t,y = oscillator(damping=.5)
        energy = .5*y[:,1]**2+2*y[:,0]**2
        self.assertTrue(np.all(np.diff(energy) < 1e-7))
        self.assertLess(energy[-1],energy[0])

    def test_lorenz_equilibrium(self):
        _,y = lorenz(initial=(0.,0.,0.))
        np.testing.assert_array_equal(y,np.zeros_like(y))

    def test_monte_carlo_reproducibility_and_degenerate_case(self):
        a=monte_carlo(seed=7)
        b=monte_carlo(seed=7)
        np.testing.assert_array_equal(a[2],b[2])
        _,_,terminal,_,_=monte_carlo(std=0.,duration=2.)
        np.testing.assert_allclose(terminal,np.cos(4.))

    def test_invalid_rigidity(self):
        with self.assertRaises(ValueError):
            monte_carlo(mean=1.,std=1.)

if __name__ == "__main__":
    unittest.main()
