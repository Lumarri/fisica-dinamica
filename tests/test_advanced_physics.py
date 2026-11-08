import unittest
import numpy as np
from scipy.constants import c, e, G
from advanced_models import barrier_amplitudes,two_body_kinematics
from catalog import MODELS, EXAMPLES
from experiments import ExperimentConfig,example_config,run_experiment
from models import SolverSettings
from particle_data import MEV_J,PARTICLES


def run_model(key,parameters=None,duration=None,seed=42):
    return run_experiment(ExperimentConfig(model=key,parameters=parameters or {},
        duration=duration if duration is not None else MODELS[key].duration,
        seed=seed,solver=SolverSettings(points=250)))


class AdvancedPhysicsTests(unittest.TestCase):
    def test_all_model_defaults_return_finite_exported_numbers(self):
        for key in MODELS:
            with self.subTest(model=key):
                r=run_model(key)
                self.assertTrue(np.isfinite(r.states).all())
                self.assertTrue(np.isfinite(r.dataframe().select_dtypes(include='number')).all().all())

    def test_all_examples_are_valid_and_reproducible_configs(self):
        self.assertEqual(len({x.key for x in EXAMPLES}),len(EXAMPLES))
        for example in EXAMPLES:
            with self.subTest(example=example.key):
                config=example_config(example.key)
                config.validate()
                self.assertEqual(config,ExperimentConfig.from_dict(config.to_dict()))
                config.solver=SolverSettings(points=200)
                result=run_experiment(config)
                self.assertTrue(np.isfinite(result.states).all())

    def test_small_pendulum_and_energy_conservation(self):
        r=run_model('pendulum',{'angle':1.,'friction':0.},duration=2.)
        exact=np.deg2rad(1.)*np.cos(np.sqrt(9.80665)*r.t)
        np.testing.assert_allclose(r.states[:,0],exact,atol=3e-6)
        energy=r.extra['energy']
        self.assertLess(np.max(abs(energy-energy[0]))/energy[0],1e-7)

    def test_double_pendulum_energy(self):
        r=run_model('double_pendulum',duration=5.)
        energy=r.extra['energy'];scale=3*9.80665
        self.assertLess(np.max(abs(energy-energy[0]))/scale,1e-7)

    def test_projectile_vacuum_solution_and_impact(self):
        r=run_model('projectile',{'density':0.,'azimuth':0.},duration=30.)
        vz=35*np.sin(np.deg2rad(40));expected=(vz+np.sqrt(vz*vz+2*9.80665*2))/9.80665
        self.assertTrue(r.extra['ground_hit'])
        self.assertAlmostEqual(r.t[-1],expected,places=8)
        self.assertLess(r.extra['analytic_error'],1e-7)

    def test_circular_kepler_orbit_and_invariants(self):
        r=run_model('orbit',{'eccentricity':0.},duration=1.)
        frame=r.dataframe();a=1e7;mu=G*5.9722e24
        np.testing.assert_allclose(frame.radius_m,a,rtol=1e-8)
        np.testing.assert_allclose(frame.specific_energy_J_kg,-mu/(2*a),rtol=1e-8)
        self.assertAlmostEqual(r.t[-1],2*np.pi*np.sqrt(a**3/mu),places=7)
        self.assertLess(np.ptp(r.extra['angular'])/r.extra['angular'][0],1e-8)

    def test_coupled_symmetric_mode(self):
        r=run_model('coupled',{'x1':1.,'x2':1.},duration=4.)
        exact=np.cos(2*r.t)
        np.testing.assert_allclose(r.states[:,0],exact,atol=1e-8)
        np.testing.assert_allclose(r.states[:,1],exact,atol=1e-8)

    def test_duffing_without_force_or_friction_conserves_energy(self):
        r=run_model('duffing',{'force':0.,'friction':0.,'alpha':1.,'position':1.},duration=10.)
        self.assertLess(np.ptp(r.extra['energy']),1e-7)

    def test_logistic_fixed_point_and_typical_chaotic_exponent(self):
        r=run_model('logistic',{'r':2.8})
        self.assertAlmostEqual(r.states[-1,0],1-1/2.8,places=10)
        self.assertAlmostEqual(r.extra['lyapunov'],np.log(.8),places=9)
        chaotic=run_model('logistic',{'r':4.})
        self.assertAlmostEqual(chaotic.extra['lyapunov'],np.log(2),delta=.06)

    def test_magnetic_helix_has_constant_energy_and_expected_period(self):
        part=PARTICLES['electron'];gamma=1+.01/part.mass_mev
        period=2*np.pi*gamma*part.mass_kg/(e*.02)
        r=run_model('em_particle',{'pitch':90.},duration=period*1e9)
        np.testing.assert_allclose(r.extra['kinetic'],.01,atol=1e-9)
        self.assertTrue(np.all(r.extra['beta']<1))
        np.testing.assert_allclose(r.dataframe()[['x_m','y_m']].iloc[-1],0.,atol=1e-9)

    def test_electric_field_changes_momentum_linearly(self):
        r=run_model('em_particle',{'species':'proton','bz':0.,'ez':100.,'pitch':0.},duration=100.)
        pz=r.dataframe().pz_MeV_c.to_numpy()
        expected=pz[0]+e*1e5*r.t*c/MEV_J
        np.testing.assert_allclose(pz,expected,rtol=1e-9,atol=1e-10)
        self.assertLess(np.max(abs(r.extra['work_residual'])),1e-7)

    def test_rutherford_energy_and_angular_momentum(self):
        r=run_model('rutherford')
        np.testing.assert_allclose(r.extra['energy']/MEV_J,5.,rtol=1e-12)
        angular=np.cross(r.states[:,:3],r.states[:,3:])
        np.testing.assert_allclose(angular,np.tile(angular[0],(len(angular),1)),rtol=1e-10,atol=1e-20)
        self.assertAlmostEqual(np.rad2deg(r.extra['scattering_angle']),48.934,delta=.01)

    def test_radioactive_population_detector_and_reproducibility(self):
        r=run_model('radioactive',{'efficiency':1.,'background':0.},duration=10.)
        self.assertAlmostEqual(r.extra['expected'][-1],5000.,places=8)
        self.assertLess(abs(r.extra['survivors'][-1]-5000),300)
        self.assertTrue(np.all(np.diff(r.extra['survivors'])<=0))
        np.testing.assert_array_equal(r.extra['events'],r.extra['detected'])
        again=run_model('radioactive',{'efficiency':1.,'background':0.},duration=10.)
        np.testing.assert_array_equal(r.extra['survivors'],again.extra['survivors'])

    def test_two_body_four_momentum_and_masses(self):
        for M,m1,m2,T in [(139.57039,105.6583755,0.,300.),(493.677,139.57039,134.9768,500.),(91187.6,.51099895,.51099895,0.)]:
            with self.subTest(mass=M):
                parent,a,b,_,_,_=two_body_kinematics(M,m1,m2,T,65.,20.)
                np.testing.assert_allclose(a+b,parent,atol=1e-8)
                self.assertAlmostEqual(a[0]**2-np.dot(a[1:],a[1:]),m1*m1,delta=1e-5)
                self.assertAlmostEqual(b[0]**2-np.dot(b[1:],b[1:]),m2*m2,delta=1e-5)
        _,_,_,pstar,_,_=two_body_kinematics(139.57039,105.6583755,0.,0.,65.,20.)
        self.assertAlmostEqual(pstar,29.792,delta=.001)

    def test_two_body_threshold_and_invalid_threshold(self):
        parent,a,b,pstar,_,_=two_body_kinematics(3.,1.,2.,5.,60.,0.)
        self.assertEqual(pstar,0.)
        np.testing.assert_allclose(a+b,parent,atol=1e-12)
        with self.assertRaises(ValueError):two_body_kinematics(2.,1.,2.,0.,60.,0.)

    def test_barrier_flux_and_regular_threshold(self):
        for energy in [1.,5.,8.,30.]:
            with self.subTest(energy=energy):
                t,r,_,_=barrier_amplitudes(energy,5.,.4)
                self.assertAlmostEqual(abs(t)**2+abs(r)**2,1.,places=11)
        t,r,_,_=barrier_amplitudes(2.,0.,.4)
        self.assertAlmostEqual(abs(t)**2,1.,places=12)
        self.assertLess(abs(r),1e-12)
        thin=barrier_amplitudes(2.,5.,.2)[0];thick=barrier_amplitudes(2.,5.,.5)[0]
        self.assertGreater(abs(thin)**2,abs(thick)**2)

    def test_legacy_project_loading_and_invalid_model_values(self):
        config=ExperimentConfig();data=config.to_dict();data['format_version']=1
        for key in ['project_name','researcher','objective','references','parameters']:data.pop(key)
        restored=ExperimentConfig.from_dict(data)
        self.assertEqual(restored.model,'oscillator')
        self.assertEqual(restored.parameters,{})
        for p in [{'width':-1.},{'unknown':3.},{'energy':float('nan')}]:
            with self.assertRaises(ValueError):run_model('quantum_barrier',p)


if __name__=='__main__':unittest.main()
