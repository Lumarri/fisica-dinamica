"""Contrastes físicos y matemáticos de los simuladores ampliados."""
import unittest
import numpy as np
from catalog import MODELS
from experiments import ExperimentConfig,run_experiment
from models import SolverSettings
from particle_simulator import elastic_pair,reflect_walls,pair_acceleration,nonoverlapping_positions
from dynamic_systems import dynamic_definition,solution,henon_orbit,parameter_sweep


def run(model,parameters=None,duration=2.,seed=42,points=250):
    return run_experiment(ExperimentConfig(model=model,parameters=parameters or {},duration=duration,
        seed=seed,solver=SolverSettings(points=points)))


class ParticleDynamicsTests(unittest.TestCase):
    def test_equal_mass_head_on_collision_exchanges_velocities(self):
        pos=np.array([[-.09,0.,0.],[.09,0.,0.]])
        vel=np.array([[1.,.2,0.],[-1.,.2,0.]])
        energy=np.sum(vel**2);momentum=vel.sum(axis=0)
        self.assertTrue(elastic_pair(pos,vel,0,1,.1))
        np.testing.assert_allclose(vel,[[-1.,.2,0.],[1.,.2,0.]])
        np.testing.assert_allclose(vel.sum(axis=0),momentum)
        self.assertAlmostEqual(np.sum(vel**2),energy)
        self.assertGreaterEqual(np.linalg.norm(pos[0]-pos[1]),.2)
        self.assertFalse(elastic_pair(pos,vel,0,1,.1))

    def test_wall_impulse_accounts_for_momentum_change(self):
        pos=np.array([[1.01,0.,0.]])
        vel=np.array([[2.,.5,0.]])
        initial=3*vel.sum(axis=0)
        impulse,vector=reflect_walls(pos,vel,1.,3.)
        np.testing.assert_allclose(vel,[[-2.,.5,0.]])
        np.testing.assert_allclose(3*vel.sum(axis=0)+vector,initial)
        self.assertEqual(impulse,12.)
        self.assertLess(pos[0,0],1.)

    def test_initial_gas_has_no_overlaps(self):
        positions=nonoverlapping_positions(60,.94,.06,np.random.default_rng(4))
        pairs=np.triu_indices(60,1)
        self.assertGreater(np.linalg.norm(positions[pairs[0]]-positions[pairs[1]],axis=1).min(),.12)
        self.assertLessEqual(np.abs(positions).max(),.94)

    def test_gas_energy_container_bounds_and_reproducibility(self):
        a=run('gas_box');b=run('gas_box')
        np.testing.assert_array_equal(a.extra['positions'],b.extra['positions'])
        np.testing.assert_allclose(a.extra['energy'],a.extra['energy'][0],rtol=2e-13)
        self.assertLess(np.max(a.extra['momentum_balance']),1e-12)
        self.assertLessEqual(np.max(np.abs(a.extra['positions'])),1-.06+1e-12)
        self.assertGreater(a.dataframe().collisions.iloc[-1],0)
        self.assertIn('t_s',a.extra['datasets']['Trayectorias de partículas'])

    def test_pair_forces_are_opposite_and_match_potential_gradient(self):
        pos=np.array([[-.4,.1,0.],[.5,-.2,.1]])
        for interaction,charges in [('gravity',np.array([1.,1.])),('electric',np.array([.2,-.2]))]:
            with self.subTest(interaction=interaction):
                acceleration,U=pair_acceleration(pos,.3,charges,1.2,.1,interaction)
                np.testing.assert_allclose(acceleration.sum(axis=0),0.,atol=1e-14)
                h=1e-6;plus=pos.copy();minus=pos.copy();plus[0,0]+=h;minus[0,0]-=h
                up=pair_acceleration(plus,.3,charges,1.2,.1,interaction)[1]
                um=pair_acceleration(minus,.3,charges,1.2,.1,interaction)[1]
                self.assertAlmostEqual(.3*acceleration[0,0],-(up-um)/(2*h),delta=1e-9)
        repulsive=pair_acceleration(pos,.3,np.array([.2,.2]),1.,.1,'electric')[0]
        self.assertLess(repulsive[0,0],0)

    def test_verlet_conserves_momentum_and_energy_converges(self):
        common={'bodies':8,'softening':.2,'rotation':.3,'charge':0.}
        coarse=run('nbody',{**common,'step':.02},duration=2.,points=200)
        fine=run('nbody',{**common,'step':.002},duration=2.,points=200)
        for result in [coarse,fine]:
            np.testing.assert_allclose(result.extra['momentum'],0.,atol=5e-15)
            angular=result.extra['angular']
            np.testing.assert_allclose(angular,np.broadcast_to(angular[0],angular.shape),atol=1e-13)
        error=lambda r:np.max(np.abs(r.extra['energy']-r.extra['energy'][0]))
        self.assertLess(error(fine),error(coarse)/8)
        self.assertIn('t_uT',fine.extra['datasets']['Trayectorias de partículas'])

    def test_van_der_pol_at_mu_zero_matches_harmonic_solution(self):
        r=run('van_der_pol',{'mu':0.,'x0':.3,'v0':.2},duration=5.)
        np.testing.assert_allclose(r.states[:,0],.3*np.cos(r.t)+.2*np.sin(r.t),atol=1e-9)

    def test_lotka_volterra_equilibrium_and_first_integral(self):
        equilibrium=run('lotka_volterra',{'prey0':4.,'predator0':2.75},duration=5.)
        np.testing.assert_allclose(equilibrium.states,np.tile([4.,2.75],(len(equilibrium.t),1)),atol=1e-10)
        orbit=run('lotka_volterra',duration=10.)
        self.assertLess(np.ptp(orbit.dataframe().first_integral),1e-8)

    def test_sir_conservation_threshold_and_neighbor_population(self):
        r=run('sir',{'infection':.05},duration=20.)
        np.testing.assert_allclose(r.states.sum(axis=1),1.,atol=1e-12)
        np.testing.assert_allclose(r.extra['perturbed'].sum(axis=1),1.,atol=1e-12)
        self.assertTrue(np.all(np.diff(r.states[:,1])<=0))
        self.assertGreaterEqual(r.states.min(),-1e-12)

    def test_henon_follows_map_and_marks_escaped_sweep_points(self):
        p=MODELS['henon'].values({'iterations':200,'discard':50})
        y=henon_orbit(p)
        np.testing.assert_allclose(y[1:,0],1-p['a']*y[:-1,0]**2+y[:-1,1])
        np.testing.assert_allclose(y[1:,1],p['b']*y[:-1,0])
        c=ExperimentConfig(model='henon',parameters={**p,'sweep_low':1.4,'sweep_high':1.5,'b':.4})
        c.validate();scan=parameter_sweep(c,c.parameters)
        self.assertTrue((scan.status!='válido').any())
        failed=scan[scan.status!='válido']
        self.assertTrue(failed['maximum'].isna().all())

    def test_uncoupled_kuramoto_is_uniform_phase_advance(self):
        p=MODELS['kuramoto'].values({'coupling':0.})
        rhs,initial,_=dynamic_definition('kuramoto',p,17)
        t=np.linspace(0,2,200);y=solution(rhs,initial,t,SolverSettings(points=200))
        omega=np.asarray(rhs(0,initial))
        np.testing.assert_allclose(y,initial[None,:]+t[:,None]*omega,atol=1e-10)
        r=run('kuramoto',{'coupling':0.},seed=17)
        order=r.dataframe().order_parameter
        self.assertTrue(order.between(0,1+1e-14).all())

    def test_sweeps_are_reproducible_and_constraints_reject_bad_joint_parameters(self):
        a=run('rossler');b=run('rossler')
        np.testing.assert_allclose(a.extra['sweep']['maximum'],b.extra['sweep']['maximum'])
        for model,p in [('gas_box',{'bodies':96,'radius':.3}),('sir',{'s0':1.,'i0':.1}),
                        ('rossler',{'sweep_low':7.,'sweep_high':2.}),('henon',{'iterations':200,'discard':190}),
                        ('nbody',{'step':.03,'softening':.03})]:
            with self.subTest(model=model),self.assertRaises(ValueError):
                ExperimentConfig(model=model,parameters=p).validate()


if __name__=='__main__':unittest.main()
