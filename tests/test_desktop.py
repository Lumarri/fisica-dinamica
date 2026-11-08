import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Qt, QEventLoop, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from desktop import MainWindow, setup_style
from experiments import ExperimentConfig, run_experiment
from models import SolverSettings
from catalog import MODELS


class DesktopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        setup_style(cls.app)

    def setUp(self):
        self.window = MainWindow(auto_run=False)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.wait_worker()
        self.window.close()
        self.app.processEvents()

    def wait_worker(self):
        if self.window.worker is None:return
        loop=QEventLoop();timer=QTimer();timer.setSingleShot(True)
        timer.timeout.connect(loop.quit);self.window.worker.finished.connect(loop.quit)
        timer.start(20000);loop.exec();timer.stop()

    def test_all_models_draw_native_scene_series_formulas_and_planes(self):
        for model in MODELS:
            with self.subTest(model=model):
                c = ExperimentConfig(model=model, duration=1, count=100,
                                     solver=SolverSettings(points=200))
                self.window.apply_config(c)
                self.window.accept_result(run_experiment(c))
                for canvas in [self.window.scene, self.window.analysis, self.window.formulas]:
                    canvas.draw()
                self.app.processEvents()
                entries=list(self.window.dynamic_fields.values())
                for i,entry in enumerate(entries):
                    for other in entries[i+1:]:self.assertFalse(entry.geometry().intersects(other.geometry()))
                self.assertEqual(len(self.window.scene.plane_artists), 3)
                self.assertEqual(self.window.dynamic_form.rowCount(),len(MODELS[model].parameters))
                if model in {'pendulum','double_pendulum','projectile','orbit','em_particle','rutherford','two_body'}:
                    ax=self.window.scene.ax
                    spans=[b-a for a,b in [ax.get_xlim(),ax.get_ylim(),ax.get_zlim()]]
                    self.assertAlmostEqual(spans[0],spans[1],places=7)
                    self.assertAlmostEqual(spans[0],spans[2],places=7)
                for name in ['Plano XY', 'Plano XZ', 'Plano YZ']:
                    self.window.view_selector.setCurrentText(name)
                self.window.planes_check.setChecked(False)
                self.assertFalse(any(a.get_visible() for a in self.window.scene.plane_artists))
                self.assertTrue(self.window.csv_button.isEnabled())
                self.assertFalse(self.window.dirty)
                self.window.timeline.setValue(100)
                prefix='n = ' if model=='logistic' else 'x = ' if model=='quantum_barrier' else 't = '
                self.assertIn(prefix, self.window.time_label.text())

    def test_background_simulation_from_run_button(self):
        c = ExperimentConfig(duration=1, solver=SolverSettings(points=200))
        self.window.apply_config(c)
        QTest.mouseClick(self.window.run_button, Qt.MouseButton.LeftButton)
        self.wait_worker()
        self.assertIsNone(self.window.worker)
        self.assertIsNotNone(self.window.result)
        self.assertFalse(self.window.dirty)
        self.assertTrue(self.window.sidebar.isEnabled())

    def test_changed_parameters_disable_stale_result_exports(self):
        c = ExperimentConfig(duration=1, solver=SolverSettings(points=200))
        self.window.apply_config(c)
        self.window.accept_result(run_experiment(c))
        self.window.fields['mass'].setValue(2.)
        self.assertTrue(self.window.dirty)
        self.assertFalse(self.window.csv_button.isEnabled())
        self.assertFalse(self.window.png_button.isEnabled())
        self.assertFalse(self.window.play_button.isEnabled())

    def test_save_load_csv_and_png_through_native_actions(self):
        c = ExperimentConfig(model='ensemble', duration=1, count=100, notes='Prueba de investigación',
                             solver=SolverSettings(points=200))
        self.window.apply_config(c)
        self.window.accept_result(run_experiment(c))
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)/'proyecto.json'
            with patch('desktop.QFileDialog.getSaveFileName', return_value=(str(project), '')):
                self.window.save_project()
            loaded = ExperimentConfig.load(project)
            self.assertEqual(loaded.seed, c.seed)
            self.assertEqual(loaded.notes, c.notes)
            csv = Path(directory)/'datos.csv'
            with patch('desktop.QFileDialog.getSaveFileName', return_value=(str(csv), '')):
                self.window.export_csv()
            self.assertTrue(csv.exists())
            self.assertTrue(csv.with_suffix('.experiment.json').exists())
            png = Path(directory)/'escena.png'
            with patch('desktop.QFileDialog.getSaveFileName', return_value=(str(png), '')):
                self.window.export_png()
            self.assertGreater(png.stat().st_size, 1000)

    def test_loaded_precision_is_not_rounded_to_a_power_of_ten(self):
        c = ExperimentConfig(solver=SolverSettings(rtol=2.5e-9, atol=3.5e-14, points=200))
        self.window.apply_config(c)
        restored = self.window.collect_config()
        self.assertEqual(restored.solver.rtol, c.solver.rtol)
        self.assertEqual(restored.solver.atol, c.solver.atol)

    def test_particle_category_and_example_load_in_worker(self):
        self.window.family_selector.setCurrentIndex(self.window.family_selector.findData('Partículas y cuántica'))
        self.assertEqual(self.window.model_selector.count(),5)
        self.window.model_selector.setCurrentIndex(self.window.model_selector.findData('em_particle'))
        self.window.example_selector.setCurrentIndex(self.window.example_selector.findData('positron_helix'))
        QTest.mouseClick(self.window.load_example_button,Qt.MouseButton.LeftButton)
        self.wait_worker()
        self.assertIsNone(self.window.worker)
        self.assertEqual(self.window.result.config.parameters['species'],'positron')
        self.assertIn('Positrón',self.window.metadata_fields['project_name'].text())

    def test_auxiliary_dataset_export_and_research_metadata(self):
        c=ExperimentConfig(model='two_body',duration=1,project_name='Pión experimental',
                           researcher='Investigador',objective='Conservar el cuatro-momento',
                           references='PDG',solver=SolverSettings(points=200))
        self.window.apply_config(c);self.window.accept_result(run_experiment(c))
        self.assertEqual(self.window.data_panel.current_frame().shape[0],3)
        self.window.data_panel.selector.setCurrentText('Barrido angular')
        self.assertEqual(self.window.data_panel.current_frame().shape[0],200)
        with tempfile.TemporaryDirectory() as directory:
            csv=Path(directory)/'angular.csv'
            with patch('desktop.QFileDialog.getSaveFileName',return_value=(str(csv),'')):
                self.window.export_csv()
            self.assertIn('cos_theta_star',csv.read_text())
            restored=ExperimentConfig.load(csv.with_suffix('.experiment.json'))
            self.assertEqual(restored.researcher,c.researcher)
            self.assertEqual(restored.parameters,self.window.result.config.parameters)

    def test_tiny_time_units_and_fields_do_not_clip_on_loading(self):
        c=ExperimentConfig(model='radioactive',duration=1e-5,parameters={'half_life':1.5e-6},
                           solver=SolverSettings(points=200))
        self.window.apply_config(c);restored=self.window.collect_config()
        self.assertEqual(restored.duration,c.duration)
        self.assertEqual(restored.parameters['half_life'],c.parameters['half_life'])


if __name__ == '__main__':
    unittest.main()
