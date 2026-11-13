import unittest
import numpy as np
from scipy.constants import m_e,c
from spatial_models import compton_kinematics,surface_mesh,mesh_area
from graph_models import make_graph
from experiments import ExperimentConfig,run_experiment
from catalog import MODELS
from models import SolverSettings
from particle_data import MEV_J


def run(name,parameters=None,duration=3.):
 return run_experiment(ExperimentConfig(model=name,parameters=parameters or {},duration=duration,solver=SolverSettings(points=220)))


class SpatialGraphTests(unittest.TestCase):
 def test_compton_four_momentum_and_electron_mass(self):
  rest=m_e*c*c/MEV_J
  for E in [.001,.5,10.]:
   for theta in [0,np.pi/2,np.pi]:
    outgoing,K,p,direction=compton_kinematics(E,theta,.7)
    np.testing.assert_allclose(outgoing*direction+p,[0,0,E],atol=1e-13)
    self.assertAlmostEqual(outgoing+K,E,places=13)
    self.assertAlmostEqual((rest+K)**2-np.dot(p,p),rest**2,delta=1e-11)
    self.assertGreaterEqual(K,0)
  photon,K,_,_=compton_kinematics(.5,0.)
  self.assertEqual(photon,.5);self.assertEqual(K,0)

 def test_pauls_zero_field_is_rectilinear(self):
  r=run('paul_trap',{'a':0.,'q':0.,'vx0':.1,'vy0':-.2,'vz0':.05})
  expected=np.array([1.,.6,.4])+r.t[:,None]*np.array([.1,-.2,.05])
  np.testing.assert_allclose(r.states[:,:3],expected,atol=1e-12)

 def test_sphere_and_torus_mesh_area_converge(self):
  for shape,exact in [('sphere',4*np.pi*1.5**2),('torus',4*np.pi**2*1.5*.4)]:
   a=mesh_area(surface_mesh(shape,1.5,.4,0,25)[0]);b=mesh_area(surface_mesh(shape,1.5,.4,0,49)[0])
   self.assertLess(abs(b-exact),abs(a-exact)/3)
   self.assertLess(abs(b-exact)/exact,.005)

 def test_mobius_seam_reverses_transverse_parameter(self):
  mesh,_,_=surface_mesh('mobius',1.5,.4,0,49)
  np.testing.assert_allclose(mesh[:,0],mesh[::-1,-1],atol=1e-14)

 def test_geodesic_radius_central_plane_and_chord(self):
  r=run('geodesic',duration=10.)
  np.testing.assert_allclose(np.linalg.norm(r.states,axis=1),1.5,atol=1e-14)
  normal=np.cross(r.states[0],r.states[1]);normal/=np.linalg.norm(normal)
  np.testing.assert_allclose(r.states@normal,0,atol=1e-13)
  np.testing.assert_allclose(r.dataframe().chord_uL,3*np.abs(np.sin(.4*r.t/2)),atol=1e-14)

 def test_all_topologies_have_symmetric_laplacian_and_reproducible_edges(self):
  for topology in ['small_world','grid','geometric','random']:
   p=MODELS['graph_heat'].values({'topology':topology,'weights':'distance'})
   a=make_graph(p,17);b=make_graph(p,17)
   np.testing.assert_array_equal(a['A'],b['A'])
   np.testing.assert_allclose(a['L'],a['L'].T)
   np.testing.assert_allclose(a['L'].sum(axis=1),0,atol=1e-13)
   self.assertGreater(np.linalg.eigvalsh(a['L']).min(),-1e-12)
   self.assertTrue(np.all(np.diag(a['A'])==0))

 def test_routes_have_correct_cost_and_detect_disconnected_destination(self):
  r=run('graph_routes',{'topology':'grid','weights':'distance'})
  path=r.extra['route'];cost=r.extra['graph']['costs']
  self.assertEqual(path[0],0);self.assertEqual(path[-1],31)
  route=r.extra['datasets']['Ruta mínima']
  self.assertAlmostEqual(route.cumulative_cost.iloc[-1],sum(cost[i,j] for i,j in zip(path[:-1],path[1:])))
  r=run('graph_routes',{'topology':'random','probability':0.})
  self.assertEqual(r.extra['route'],[]);self.assertEqual(r.extra['graph']['components'],32)
  self.assertEqual(r.dataframe().reachable.sum(),1)

 def test_heat_conserves_total_and_variance_decreases(self):
  r=run('graph_heat',{'topology':'grid'},duration=15.)
  np.testing.assert_allclose(r.states.sum(axis=1),1.,atol=1e-13)
  self.assertTrue(np.all(np.diff(r.states.var(axis=1))<=1e-14))
  self.assertGreater(r.states.min(),-1e-13)
  isolated=run('graph_heat',{'topology':'random','probability':0.})
  np.testing.assert_array_equal(isolated.states[:,0],1.)
  np.testing.assert_array_equal(isolated.states[:,1:],0.)

 def test_network_energy_conservation_and_dissipation(self):
  free=run('graph_waves',{'topology':'grid','damping':0.},duration=8.)
  self.assertLess(np.ptp(free.extra['energy']),1e-8)
  damped=run('graph_waves',{'damping':.3},duration=8.)
  self.assertTrue(np.all(np.diff(damped.extra['energy'])<1e-12))
  self.assertLess(damped.extra['energy'][-1],damped.extra['energy'][0])

 def test_isolated_network_node_matches_harmonic_solution(self):
  r=run('graph_waves',{'topology':'random','probability':0.,'damping':0.,'anchor':4.,'node_mass':1.})
  np.testing.assert_allclose(r.states[:,0],.6*np.cos(2*r.t),atol=1e-9)
  np.testing.assert_allclose(r.states[:,1:32],0.,atol=1e-14)

 def test_joint_geometry_and_graph_constraints(self):
  for name,p in [('surface',{'shape':'torus','minor':2.,'radius':1.}),('surface',{'shape':'mobius','minor':1.,'radius':1.}),
                 ('graph_routes',{'nodes':6,'source':7}),('graph_heat',{'nodes':6,'neighbors':3})]:
   with self.subTest(model=name),self.assertRaises(ValueError):ExperimentConfig(model=name,parameters=p).validate()


if __name__=='__main__':unittest.main()
