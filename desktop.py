"""Ventana nativa Qt del laboratorio DYNAMIS."""
import html
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QColor, QFont, QPalette, QValidator
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
    QFormLayout, QFrame, QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPushButton, QScrollArea, QSlider, QSpinBox, QSplitter,
    QTabWidget, QTextBrowser, QTextEdit, QVBoxLayout, QWidget,
)
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

from experiments import ExperimentConfig, MODEL_NAMES, run_experiment
from models import SolverSettings
from plotting import AnalysisCanvas, FormulaCanvas, SceneCanvas

STYLE = """
QWidget { color: #e2eaf5; font-family: 'Segoe UI', 'DejaVu Sans'; font-size: 12px; }
QMainWindow, QWidget#root { background: #0b1320; }
QFrame#header { background: #0e192a; border-bottom: 1px solid #25344a; }
QFrame#sidebar { background: #101c2e; border: 1px solid #26364d; border-radius: 10px; }
QLabel#brand { font-size: 22px; font-weight: 700; color: #57d9d0; }
QLabel#eyebrow { color: #57d9d0; font-size: 10px; font-weight: 700; }
QLabel#title { font-size: 24px; font-weight: 600; }
QLabel#muted { color: #91a6c0; font-size: 11px; }
QLabel#status { color: #efba6b; padding: 5px; }
QGroupBox { border: 1px solid #2a3a51; border-radius: 7px; margin-top: 15px; padding: 12px 9px 7px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; color: #a6bad4; }
QComboBox, QDoubleSpinBox, QSpinBox { background: #0c1626; border: 1px solid #33445d; border-radius: 5px; padding: 6px; min-height: 17px; }
QComboBox::drop-down { width: 18px; border: none; }
QComboBox QAbstractItemView { background: #142238; selection-background-color: #22515a; }
QPushButton { background: #1b2c43; border: 1px solid #34475f; padding: 8px 13px; border-radius: 6px; }
QPushButton:hover { background: #293f5b; border-color: #57d9d0; }
QPushButton:disabled { color: #586c86; border-color: #25344a; }
QPushButton#primary { background: #57d9d0; color: #0a2029; font-weight: 700; border: none; min-height: 24px; }
QPushButton#primary:hover { background: #87ede5; }
QPushButton#primary:disabled { background: #24434d; color: #78959f; }
QFrame#metric { background: #111e31; border: 1px solid #293a51; border-radius: 8px; }
QLabel#metricvalue { color: #e6f4fa; font-size: 21px; font-weight: 600; }
QLabel#metriclabel { color: #91a6c0; font-size: 10px; }
QTabWidget::pane { border: 1px solid #293a51; border-radius: 7px; background: #111c2e; }
QTabBar::tab { padding: 10px 15px; color: #95aac6; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #57d9d0; border-bottom-color: #57d9d0; }
QTextEdit, QTextBrowser { background: #111c2e; border: 1px solid #2a3b53; border-radius: 6px; padding: 10px; selection-background-color: #22515a; }
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical { width: 9px; background: #0e192a; }
QScrollBar::handle:vertical { background: #34475f; min-height: 25px; border-radius: 4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QSlider::groove:horizontal { height: 4px; background: #2a3d57; border-radius: 2px; }
QSlider::handle:horizontal { width: 12px; height: 12px; margin: -4px 0; background: #57d9d0; border-radius: 6px; }
QToolBar { border: none; background: #111c2e; }
QToolButton { padding: 4px; background: transparent; }
QMenuBar, QMenu { background: #111c2e; }
QMenu::item:selected { background: #24434d; }
QStatusBar { color: #91a6c0; background: #0e192a; }
"""


def setup_style(app):
    app.setStyle("Fusion")
    palette = QPalette()
    for role, color in [(QPalette.ColorRole.Window, '#0b1320'),
                        (QPalette.ColorRole.WindowText, '#e2eaf5'),
                        (QPalette.ColorRole.Base, '#111c2e'),
                        (QPalette.ColorRole.Text, '#e2eaf5'),
                        (QPalette.ColorRole.Button, '#1b2c43'),
                        (QPalette.ColorRole.ButtonText, '#e2eaf5'),
                        (QPalette.ColorRole.Highlight, '#22515a')]:
        palette.setColor(role, QColor(color))
    app.setPalette(palette)
    app.setFont(QFont('Segoe UI', 10))
    app.setStyleSheet(STYLE)


class SimulationWorker(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config

    def run(self):
        try:
            self.completed.emit(run_experiment(self.config))
        except Exception as error:
            self.failed.emit(str(error))


class ScientificNumber(QDoubleSpinBox):
    """Entrada compacta que admite notación científica sin ocultar decimales."""
    def textFromValue(self, value):
        return format(value, '.14g')

    def valueFromText(self, text):
        try:
            return float(text.strip().replace(',', '.'))
        except ValueError:
            return self.value()

    def validate(self, text, position):
        try:
            value = float(text.replace(',', '.'))
        except ValueError:
            return QValidator.State.Intermediate, text, position
        state = QValidator.State.Acceptable if np.isfinite(value) and self.minimum() <= value <= self.maximum() else QValidator.State.Intermediate
        return state, text, position


class Metric(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName('metric')
        box = QVBoxLayout(self)
        box.setContentsMargins(14, 10, 14, 10)
        self.value = QLabel('—'); self.value.setObjectName('metricvalue')
        self.label = QLabel('Esperando simulación'); self.label.setObjectName('metriclabel')
        self.label.setWordWrap(True)
        box.addWidget(self.value); box.addWidget(self.label)

    def set(self, value, label):
        self.value.setText(str(value)); self.label.setText(label)


class MainWindow(QMainWindow):
    def __init__(self, *, auto_run=True):
        super().__init__()
        self.setWindowTitle('DYNAMIS · Física y sistemas dinámicos')
        self.resize(1460, 940)
        self.setMinimumSize(1080, 740)
        self.result = None
        self.worker = None
        self.loading = True
        self.dirty = True
        self.fields = {}
        self.timer = QTimer(self)
        self.timer.setInterval(65)
        self.timer.timeout.connect(self._advance_frame)
        self._build_menu()
        root = QWidget(); root.setObjectName('root'); self.setCentralWidget(root)
        layout = QVBoxLayout(root); layout.setContentsMargins(16, 0, 16, 8); layout.setSpacing(12)
        layout.addWidget(self._build_header())
        content = QSplitter(Qt.Orientation.Horizontal)
        self.sidebar = self._build_sidebar()
        content.addWidget(self.sidebar)
        content.addWidget(self._build_workspace())
        content.setSizes([295, 1120]); content.setChildrenCollapsible(False)
        layout.addWidget(content, 1)
        self.statusBar().showMessage('Ventana nativa · datos y proyectos locales · aritmética float64')
        self.loading = False
        self._model_changed()
        if auto_run:
            QTimer.singleShot(80, self.run_simulation)

    def _build_menu(self):
        menu = self.menuBar().addMenu('Archivo')
        for title, shortcut, callback in [('Abrir proyecto…', 'Ctrl+O', self.open_project),
                                           ('Guardar proyecto…', 'Ctrl+S', self.save_project),
                                           ('Exportar resultados CSV…', 'Ctrl+E', self.export_csv),
                                           ('Exportar figura PNG…', 'Ctrl+Shift+S', self.export_png)]:
            action = QAction(title, self); action.setShortcut(shortcut); action.triggered.connect(callback)
            menu.addAction(action)
        menu.addSeparator()
        menu.addAction('Salir', self.close)

    def _build_header(self):
        header = QFrame(); header.setObjectName('header')
        box = QHBoxLayout(header); box.setContentsMargins(10, 14, 10, 14)
        brand = QLabel('DYNAMIS'); brand.setObjectName('brand')
        box.addWidget(brand)
        subtitle = QLabel('LABORATORIO DE FÍSICA\nSistemas dinámicos e incertidumbre'); subtitle.setObjectName('muted')
        box.addSpacing(14); box.addWidget(subtitle); box.addStretch()
        for title, callback in [('Abrir proyecto', self.open_project), ('Guardar proyecto', self.save_project)]:
            button = QPushButton(title); button.clicked.connect(callback); box.addWidget(button)
        return header

    def _number(self, key, value, low, high, decimals=3, step=.1, integer=False):
        if integer:
            widget = QSpinBox(); widget.setRange(int(low), int(high)); widget.setSingleStep(int(step))
        else:
            widget = ScientificNumber(); widget.setDecimals(20); widget.setRange(low, high); widget.setSingleStep(step)
        widget.setValue(value); widget.setKeyboardTracking(False)
        widget.setMinimumWidth(100)
        widget.valueChanged.connect(self._mark_dirty)
        self.fields[key] = widget
        return widget

    def _group(self, title):
        group = QGroupBox(title)
        form = QFormLayout(group)
        form.setSpacing(8); form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.side_layout.addWidget(group)
        return group, form

    def _build_sidebar(self):
        outer = QFrame(); outer.setObjectName('sidebar'); outer.setMinimumWidth(278); outer.setMaximumWidth(390)
        box = QVBoxLayout(outer); box.setContentsMargins(10, 12, 10, 10)
        eyebrow = QLabel('01 / CONFIGURAR EXPERIMENTO'); eyebrow.setObjectName('eyebrow'); box.addWidget(eyebrow)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        body = QWidget(); self.side_layout = QVBoxLayout(body); self.side_layout.setContentsMargins(2, 0, 2, 0)
        self.model_selector = QComboBox()
        for key, name in MODEL_NAMES.items():
            self.model_selector.addItem(name, key)
        self.model_selector.currentIndexChanged.connect(self._model_changed)
        self.side_layout.addWidget(self.model_selector)
        _, general = self._group('Tiempo')
        general.addRow('Duración T', self._number('duration', 25., .5, 120., step=1))
        label = QLabel('Segundos; Lorenz usa tiempo adimensional.'); label.setObjectName('muted'); label.setWordWrap(True)
        general.addRow(label)
        self.physical_group, self.physical_form = self._group('Parámetros físicos · SI')
        self.physical_form.addRow('Masa m (kg)', self._number('mass', 1., .05, 100.))
        self.physical_form.addRow('Rigidez k (N/m)', self._number('stiffness', 4., .05, 100.))
        self.physical_form.addRow('Amortig. c (kg/s)', self._number('damping', .2, 0., 30.))
        self.lorenz_group, form = self._group('Parámetros de Lorenz')
        for key, label, val, low, high in [('sigma', 'σ', 10., .1, 50.), ('rho', 'ρ', 28., 0., 100.),
                                           ('beta', 'β', 8/3, .1, 10.)]:
            form.addRow(label, self._number(key, val, low, high, decimals=6))
        form.addRow('Perturbación Δx', self._number('delta', .0001, 1e-8, 1., decimals=8, step=.0001))
        _, self.initial_form = self._group('Condiciones iniciales')
        for key, label, val in [('x0', 'x₀ (m)', 1.), ('v0', 'v₀ (m/s)', 0.), ('y0', 'y₀', 1.), ('z0', 'z₀', 1.)]:
            self.initial_form.addRow(label, self._number(key, val, -100., 100., decimals=6))
        self.ensemble_group, form = self._group('Conjunto probabilístico')
        form.addRow('Desv. k (N/m)', self._number('stiffness_std', .4, 0., 10.))
        form.addRow('Desv. x₀ (m)', self._number('position_std', .05, 0., 10.))
        form.addRow('Realizaciones N', self._number('count', 1000, 100, 10000, step=100, integer=True))
        form.addRow('Semilla', self._number('seed', 42, 0, 2147483647, step=1, integer=True))
        form.addRow('Umbral a (m)', self._number('threshold', .5, -100., 100.))
        note = QLabel('K y X₀ uniformes e independientes.\nEste conjunto usa c = 0.'); note.setObjectName('muted'); note.setWordWrap(True); form.addRow(note)
        self.solver_group, self.solver_form = self._group('Precisión y muestreo')
        self.solver_form.addRow('Tolerancia rtol', self._number('rtol', 1e-9, 1e-12, 1e-3, step=1e-9))
        self.solver_form.addRow('Tolerancia atol', self._number('atol', 1e-11, 1e-14, 1e-3, step=1e-11))
        self.solver_form.addRow('Paso máximo', self._number('max_step', .05, .001, 2., decimals=3, step=.01))
        self.solver_form.addRow('Puntos temporales', self._number('points', 1200, 200, 3000, step=100, integer=True))
        self.side_layout.addStretch()
        scroll.setWidget(body); box.addWidget(scroll, 1)
        self.run_button = QPushButton('Simular experimento'); self.run_button.setObjectName('primary')
        self.run_button.clicked.connect(self.run_simulation); box.addWidget(self.run_button)
        return outer

    def _build_workspace(self):
        area = QWidget(); box = QVBoxLayout(area); box.setContentsMargins(10, 0, 0, 0); box.setSpacing(9)
        eyebrow = QLabel('02 / OBSERVAR · MEDIR · CONTRASTAR'); eyebrow.setObjectName('eyebrow'); box.addWidget(eyebrow)
        title = QLabel('Explora el movimiento.'); title.setObjectName('title'); box.addWidget(title)
        self.experiment_label = QLabel('Configura un experimento y pulsa Simular.'); self.experiment_label.setObjectName('muted'); box.addWidget(self.experiment_label)
        cards = QHBoxLayout(); cards.setSpacing(9); self.metrics = [Metric() for _ in range(4)]
        for card in self.metrics:
            cards.addWidget(card)
        box.addLayout(cards)
        self.tabs = QTabWidget()
        scene_page = QWidget(); scene_layout = QVBoxLayout(scene_page); scene_layout.setContentsMargins(8, 7, 8, 7)
        controls = QHBoxLayout()
        controls.addWidget(QLabel('Vista'))
        self.view_selector = QComboBox(); self.view_selector.addItems(['Perspectiva', 'Plano XY', 'Plano XZ', 'Plano YZ'])
        controls.addWidget(self.view_selector)
        self.planes_check = QCheckBox('Planos de referencia'); self.planes_check.setChecked(True); controls.addWidget(self.planes_check)
        controls.addStretch()
        self.png_button = QPushButton('Exportar PNG'); self.png_button.clicked.connect(self.export_png); self.png_button.setEnabled(False); controls.addWidget(self.png_button)
        scene_layout.addLayout(controls)
        self.scene = SceneCanvas(); scene_layout.addWidget(self.scene, 1)
        self.view_selector.currentTextChanged.connect(self.scene.view)
        self.planes_check.toggled.connect(self.scene.show_planes)
        toolbar = NavigationToolbar2QT(self.scene, scene_page); scene_layout.addWidget(toolbar)
        self.scene_note = QLabel('Arrastra para girar la escena. Rueda o herramientas de la figura para acercar.'); self.scene_note.setObjectName('muted'); self.scene_note.setWordWrap(True); scene_layout.addWidget(self.scene_note)
        timeline = QHBoxLayout()
        self.play_button = QPushButton('Reproducir'); self.play_button.setEnabled(False); self.play_button.clicked.connect(self._toggle_play)
        timeline.addWidget(self.play_button)
        self.timeline = QSlider(Qt.Orientation.Horizontal); self.timeline.setRange(0, 0); self.timeline.valueChanged.connect(self._seek); timeline.addWidget(self.timeline, 1)
        self.time_label = QLabel('t = 0'); self.time_label.setMinimumWidth(120); timeline.addWidget(self.time_label)
        scene_layout.addLayout(timeline)
        self.tabs.addTab(scene_page, 'Escena 3D')
        analysis_page = QWidget(); analysis_layout = QVBoxLayout(analysis_page)
        self.analysis = AnalysisCanvas(); analysis_layout.addWidget(self.analysis, 1)
        analysis_layout.addWidget(NavigationToolbar2QT(self.analysis, analysis_page))
        self.tabs.addTab(analysis_page, 'Series y estadística')
        formulas_page = QWidget(); formulas_layout = QVBoxLayout(formulas_page)
        self.formulas = FormulaCanvas(); formulas_layout.addWidget(self.formulas, 2)
        self.precision_text = QTextBrowser(); self.precision_text.setMinimumHeight(155); formulas_layout.addWidget(self.precision_text, 1)
        self.tabs.addTab(formulas_page, 'Fórmulas y precisión')
        notebook = QWidget(); notebook_box = QVBoxLayout(notebook)
        notebook_box.addWidget(QLabel('Hipótesis, supuestos, fuentes y observaciones'))
        self.notes = QTextEdit(); self.notes.setPlaceholderText('Pregunta de investigación:\n\nHipótesis:\n\nSupuestos del modelo:\n\nFuentes / referencias:\n\nObservaciones y próximos experimentos:')
        notebook_box.addWidget(self.notes, 1)
        note = QLabel('Las notas se guardan junto con parámetros, tolerancias y semilla en el proyecto JSON.'); note.setWordWrap(True); note.setObjectName('muted'); notebook_box.addWidget(note)
        self.tabs.addTab(notebook, 'Cuaderno')
        box.addWidget(self.tabs, 1)
        footer = QHBoxLayout()
        self.state_label = QLabel('Preparado'); self.state_label.setObjectName('status'); footer.addWidget(self.state_label, 1)
        self.csv_button = QPushButton('Exportar CSV + configuración'); self.csv_button.setEnabled(False); self.csv_button.clicked.connect(self.export_csv); footer.addWidget(self.csv_button)
        box.addLayout(footer)
        return area

    def _model_changed(self, *_):
        if self.loading:
            return
        model = self.model_selector.currentData()
        self.physical_group.setVisible(model != 'lorenz')
        self.physical_form.setRowVisible(self.fields['damping'], model == 'oscillator')
        self.lorenz_group.setVisible(model == 'lorenz')
        self.ensemble_group.setVisible(model == 'ensemble')
        self.initial_form.setRowVisible(self.fields['v0'], model != 'lorenz')
        self.initial_form.setRowVisible(self.fields['y0'], model == 'lorenz')
        self.initial_form.setRowVisible(self.fields['z0'], model == 'lorenz')
        self.initial_form.labelForField(self.fields['x0']).setText('x₀' if model == 'lorenz' else 'x₀ (m)')
        for key in ['rtol', 'atol', 'max_step']:
            self.solver_form.setRowVisible(self.fields[key], model != 'ensemble')
        self._mark_dirty()

    def _mark_dirty(self, *_):
        if self.loading:
            return
        self.dirty = True
        self.timer.stop()
        self.play_button.setText('Reproducir')
        self.play_button.setEnabled(False)
        self.csv_button.setEnabled(False); self.png_button.setEnabled(False)
        self.state_label.setText('Parámetros pendientes · pulsa Simular para actualizar las figuras')

    def collect_config(self):
        values = {k: w.value() for k, w in self.fields.items()}
        solver = SolverSettings(rtol=values.pop('rtol'),
                                atol=values.pop('atol'),
                                max_step=values.pop('max_step'), points=values.pop('points'))
        if self.model_selector.currentData() == 'ensemble':
            values['damping'] = 0.
        config = ExperimentConfig(model=self.model_selector.currentData(), solver=solver,
                                  notes=self.notes.toPlainText(), **values)
        config.validate()
        return config

    @Slot()
    def run_simulation(self):
        if self.worker is not None:
            return
        try:
            config = self.collect_config()
        except ValueError as error:
            self.state_label.setText(str(error)); return
        self.timer.stop(); self.play_button.setText('Reproducir'); self.play_button.setEnabled(False)
        self.csv_button.setEnabled(False); self.png_button.setEnabled(False)
        self.sidebar.setEnabled(False)
        self.state_label.setText('Calculando… la ventana permanece disponible')
        self.worker = SimulationWorker(config, self)
        self.worker.completed.connect(self.accept_result)
        self.worker.failed.connect(self._calculation_failed)
        self.worker.finished.connect(self._worker_finished)
        self.worker.start()

    @Slot(object)
    def accept_result(self, result):
        self.result = result
        self.scene.draw_result(result); self.analysis.draw_result(result); self.formulas.draw_result(result)
        self.scene.view(self.view_selector.currentText())
        self._show_precision(result); self._show_metrics(result)
        self.timeline.setRange(0, len(result.t)-1); self.timeline.setValue(0); self._seek(0)
        model = result.config.model
        descriptions = {'oscillator': 'Espacio de fases ampliado: (x, v, t). El tercer eje es tiempo, no una dimensión espacial.',
                        'lorenz': 'Espacio de estados (x, y, z), adimensional. La línea ámbar es una condición inicial vecina.',
                        'ensemble': 'Conjunto en (x, v, t). Curvas azules: hasta 24 realizaciones; línea central: parámetros nominales.'}
        self.scene_note.setText(descriptions[model]+' Arrastra para girar; usa las herramientas para acercar.')
        self.experiment_label.setText(MODEL_NAMES[model]+' · '+str(result.config.solver.points)+' puntos temporales')
        self.state_label.setText('Resultados actualizados · solución analítica y muestreo reproducible' if model == 'ensemble'
                                 else 'Resultados actualizados · DOP853 y comparación con tolerancias más estrictas')
        self.dirty = False
        self.play_button.setEnabled(True); self.csv_button.setEnabled(True); self.png_button.setEnabled(True)

    @Slot(str)
    def _calculation_failed(self, message):
        self.dirty = True
        self.state_label.setText('No se completó el cálculo: '+message)

    @Slot()
    def _worker_finished(self):
        thread = self.worker
        self.worker = None
        self.sidebar.setEnabled(True)
        if thread is not None:
            thread.deleteLater()

    def _show_metrics(self, r):
        c, e = r.config, r.extra
        if c.model == 'oscillator':
            energy0 = e['energy'][0]
            ratio = e['energy'][-1]/energy0 if energy0 > 0 else 0.
            values = [(f'{np.sqrt(c.stiffness/c.mass):.4g}', 'Frecuencia natural ω₀ · rad/s'),
                      (f'{np.max(np.abs(r.states[:, 0])):.5g}', 'Pico |x| muestreado · m'),
                      (f'{ratio:.5g}', 'Energía final / energía inicial' if energy0 > 0 else 'Energía inicial y final nulas'),
                      (f"{e['scaled_difference']:.2e}", 'Diferencia normalizada al refinar')]
        elif c.model == 'lorenz':
            values = [(f'{c.rho:.5g}', 'Parámetro de control ρ'), (f'{c.delta:.2e}', 'Perturbación inicial Δx'),
                      (f"{e['separation'][-1]:.4g}", 'Separación final de estados'),
                      (f"{e['scaled_difference']:.2e}", 'Diferencia normalizada al refinar')]
        else:
            lo, hi = e['interval']
            values = [(f"{e['probability']:.2%}", 'Probabilidad estimada P[x(T) > a]'),
                      (f'{lo:.1%} – {hi:.1%}', 'Intervalo de confianza Wilson · 95 %'),
                      (str(c.count), 'Realizaciones del conjunto'), (str(c.seed), 'Semilla reproducible')]
        for metric, pair in zip(self.metrics, values):
            metric.set(*pair)

    def _show_precision(self, r):
        c, e = r.config, r.extra
        if c.model == 'ensemble':
            lo, hi = e['interval']
            body = (f'<b>Solución analítica + Monte Carlo</b><br>Float64; N = {c.count}; semilla = {c.seed}. '
                    'Las tolerancias del integrador no intervienen en este modelo analítico.<br>'
                    f'Probabilidad estimada: {e["probability"]:.6g}. Wilson 95 %: [{lo:.6g}, {hi:.6g}]. '
                    f'Error estándar aproximado: {e["standard_error"]:.4g}.<br>'
                    'Las bandas 2.5–97.5 % representan dispersión de realizaciones, no un intervalo de confianza de la media. '
                    'Si no observas ningún éxito, la probabilidad no queda demostrada como cero. '
                    'La cobertura es aproximada; los intervalos de la gráfica corresponden a cada N, no a una banda simultánea.')
        else:
            s = c.solver
            labels = ['x (m)', 'v (m/s)'] if c.model == 'oscillator' else ['x', 'y', 'z']
            differences = '; '.join(f'{label}: {value:.6g}' for label, value in zip(labels, e['absolute_difference']))
            body = (f'<b>DOP853 · float64</b><br>rtol = {s.rtol:.0e}; atol = {s.atol:.0e}; paso máximo = {s.max_step:g}. '
                    f'Muestreo: {s.points} puntos.<br>'
                    'Se repite la integración con rtol/10, atol/10 y paso máximo/2. '
                    f'Máximas diferencias absolutas por variable: {html.escape(differences)}.<br>'
                    f'Diferencia normalizada máxima: {e["scaled_difference"]:.6g}. '
                    'Cada componente se escala por max(1, máximo absoluto de la referencia).<br>'
                    'Esta comparación es un diagnóstico empírico, no una cota garantizada del error. '
                    'La escala local de control es atol + rtol·|y|; más puntos de salida no equivalen a mayor precisión. ')
            if 'analytic_error' in e:
                body += f'Error máximo de x frente a la solución analítica: {e["analytic_error"]:.6g} m. '
            if c.model == 'lorenz':
                body += 'En regímenes caóticos, dos aproximaciones pueden separarse mucho a tiempos largos. '
        self.precision_text.setHtml('<div style="color:#c4d3e7; line-height:1.5">'+body+'</div>')

    def _toggle_play(self):
        if self.result is None or self.dirty:
            return
        if self.timer.isActive():
            self.timer.stop(); self.play_button.setText('Reproducir')
        else:
            if self.timeline.value() == self.timeline.maximum():
                self.timeline.setValue(0)
            self.timer.start(); self.play_button.setText('Pausar')

    def _advance_frame(self):
        index = min(self.timeline.maximum(), self.timeline.value()+max(1, self.timeline.maximum()//160))
        self.timeline.setValue(index)
        if index == self.timeline.maximum():
            self.timer.stop(); self.play_button.setText('Reproducir')

    def _seek(self, index):
        if self.result is not None:
            self.scene.set_frame(index)
            units = '' if self.result.config.model == 'lorenz' else ' s'
            self.time_label.setText(f't = {self.result.t[index]:.3f}'+units)

    def save_project(self):
        try:
            config = self.collect_config()
            path, _ = QFileDialog.getSaveFileName(self, 'Guardar proyecto', 'experimento.json', 'Proyecto JSON (*.json)')
            if path:
                config.save(path); self.statusBar().showMessage('Proyecto guardado: '+path, 8000)
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, 'No se pudo guardar', str(error))

    def open_project(self):
        if self.worker is not None:
            self.state_label.setText('Espera a que termine el cálculo para abrir otro proyecto.'); return
        path, _ = QFileDialog.getOpenFileName(self, 'Abrir proyecto', '', 'Proyecto JSON (*.json)')
        if not path:
            return
        try:
            self.apply_config(ExperimentConfig.load(path))
            self.run_simulation()
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, 'No se pudo abrir', str(error))

    def apply_config(self, config):
        config.validate()
        self.loading = True
        self.model_selector.setCurrentIndex(self.model_selector.findData(config.model))
        for key, widget in self.fields.items():
            if hasattr(config, key):
                widget.setValue(getattr(config, key))
        self.fields['rtol'].setValue(config.solver.rtol)
        self.fields['atol'].setValue(config.solver.atol)
        self.fields['max_step'].setValue(config.solver.max_step)
        self.fields['points'].setValue(config.solver.points)
        self.notes.setPlainText(config.notes)
        self.loading = False
        self._model_changed()

    def export_csv(self):
        if self.result is None or self.dirty or self.worker is not None:
            self.state_label.setText('Simula los parámetros actuales antes de exportar.'); return
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar resultados', 'resultados.csv', 'Datos CSV (*.csv)')
        if not path:
            return
        try:
            self.result.dataframe().to_csv(path, index=False, float_format='%.17g')
            self.result.config.notes = self.notes.toPlainText()
            self.result.config.save(Path(path).with_suffix('.experiment.json'))
            self.statusBar().showMessage('CSV y configuración guardados: '+path, 8000)
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, 'No se pudo exportar', str(error))

    def export_png(self):
        if self.result is None or self.dirty or self.worker is not None:
            self.state_label.setText('Simula los parámetros actuales antes de exportar.'); return
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar figura', 'figura.png', 'Imagen PNG (*.png)')
        if path:
            try:
                canvas = self.analysis if self.tabs.currentIndex() == 1 else self.scene
                canvas.figure.savefig(path, dpi=220, facecolor=canvas.figure.get_facecolor())
                self.statusBar().showMessage('Figura exportada: '+path, 8000)
            except OSError as error:
                QMessageBox.warning(self, 'No se pudo exportar', str(error))

    def closeEvent(self, event):
        if self.worker is not None:
            self.state_label.setText('El cálculo está terminando. Podrás cerrar la ventana al finalizar.'); event.ignore()
        else:
            self.timer.stop(); event.accept()
