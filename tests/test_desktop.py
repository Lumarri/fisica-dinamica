import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from desktop import MainWindow, setup_style
from experiments import ExperimentConfig, run_experiment
from models import SolverSettings


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
        deadline = time.monotonic()+15
        while self.window.worker is not None and time.monotonic() < deadline:
            QTest.qWait(20)
        self.window.close()
        self.app.processEvents()

    def test_all_models_draw_native_scene_series_formulas_and_planes(self):
        for model in ['oscillator', 'lorenz', 'ensemble']:
            with self.subTest(model=model):
                c = ExperimentConfig(model=model, duration=1, count=100,
                                     solver=SolverSettings(points=200))
                self.window.apply_config(c)
                self.window.accept_result(run_experiment(c))
                for canvas in [self.window.scene, self.window.analysis, self.window.formulas]:
                    canvas.draw()
                self.assertEqual(len(self.window.scene.plane_artists), 3)
                for name in ['Plano XY', 'Plano XZ', 'Plano YZ']:
                    self.window.view_selector.setCurrentText(name)
                self.window.planes_check.setChecked(False)
                self.assertFalse(any(a.get_visible() for a in self.window.scene.plane_artists))
                self.assertTrue(self.window.csv_button.isEnabled())
                self.assertFalse(self.window.dirty)
                self.window.timeline.setValue(100)
                self.assertIn('t = ', self.window.time_label.text())

    def test_background_simulation_from_run_button(self):
        c = ExperimentConfig(duration=1, solver=SolverSettings(points=200))
        self.window.apply_config(c)
        QTest.mouseClick(self.window.run_button, Qt.MouseButton.LeftButton)
        deadline = time.monotonic()+20
        while self.window.worker is not None and time.monotonic() < deadline:
            QTest.qWait(20)
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


if __name__ == '__main__':
    unittest.main()
