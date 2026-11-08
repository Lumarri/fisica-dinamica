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
    QTabWidget, QTextBrowser, QTextEdit, QVBoxLayout, QWidget, QLineEdit, QButtonGroup,
)
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

from experiments import ExperimentConfig, MODEL_NAMES, run_experiment, example_config
from catalog import MODELS, EXAMPLES
from panels import DatasetPanel, GuidePanel, ParticlePanel
from dashboard import Dashboard
from models import SolverSettings
from plotting import AnalysisCanvas, FormulaCanvas, SceneCanvas
from theme import setup_style, NeoSurface, NeoButton as QPushButton, NeoTabBar, NeoSlider as QSlider, LatexNumber

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


class Metric(NeoSurface):
    def __init__(self):
        super().__init__()
        self.setObjectName('metric')
        box = QVBoxLayout(self)
        box.setContentsMargins(14, 10, 14, 10)
        self.value = LatexNumber('—'); self.value.setObjectName('metricvalue')
        self.label = QLabel('Esperando simulación'); self.label.setObjectName('metriclabel')
        self.label.setWordWrap(True)
        box.addWidget(self.value); box.addWidget(self.label)

    def set(self, value, label):
        self.value.setText(str(value)); self.label.setText(label)


class Workspace(QWidget):
    """Permite ajustar el lienzo al panel sin forzar su altura preferida."""
    def hasHeightForWidth(self):return False

    def heightForWidth(self,width):return -1


class MainWindow(QMainWindow):
    def __init__(self, *, auto_run=True):
        super().__init__()
        self.setWindowTitle('DYNAMIS 2 · Física, dinámica y partículas')
        self.setMinimumSize(1000,640)
        screen=QApplication.primaryScreen()
        available=screen.availableGeometry() if screen is not None else None
        self.resize(min(1460,max(1000,available.width()-48)) if available else 1460,
                    min(940,max(640,available.height()-55)) if available else 940)
        self.result = None
        self.worker = None
        self.loading = True
        self.dirty = True
        self.fields = {}
        self.dynamic_fields = {}
        self._last_model = None
        self.timer = QTimer(self)
        self.timer.setInterval(65)
        self.timer.timeout.connect(self._advance_frame)
        self._build_menu()
        root = QWidget(); root.setObjectName('root'); self.setCentralWidget(root)
        layout = QVBoxLayout(root); layout.setContentsMargins(16, 0, 16, 8); layout.setSpacing(12)
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_navigation())
        content = QSplitter(Qt.Orientation.Horizontal); self.content_splitter=content
        self.sidebar = self._build_sidebar()
        content.addWidget(self.sidebar)
        self.workspace_scroll=QScrollArea();self.workspace_scroll.setWidgetResizable(True)
        self.workspace_scroll.setWidget(self._build_workspace());content.addWidget(self.workspace_scroll)
        content.setSizes([295, 1120]); content.setChildrenCollapsible(False)
        layout.addWidget(content, 1)
        self.statusBar().showMessage('Espacio de trabajo local · 15 modelos · proyectos y datos en tu equipo')
        self.loading = False
        self._model_changed()
        self.navigate_section('inicio')
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

    def _build_navigation(self):
        frame=NeoSurface();layout=QHBoxLayout(frame);layout.setContentsMargins(12,9,12,9);layout.setSpacing(7)
        self.nav_buttons={};self.nav_group=QButtonGroup(self)
        for key,title in [('inicio','Inicio'),('laboratorio','Laboratorio'),('modelos','Modelos y ejemplos'),('particulas','Partículas'),('resultados','Resultados'),('cuaderno','Cuaderno')]:
            button=QPushButton(title);button.setCheckable(True)
            button.clicked.connect(lambda checked=False,name=key:self.navigate_section(name))
            self.nav_group.addButton(button);self.nav_buttons[key]=button;layout.addWidget(button,1)
        return frame

    def navigate_section(self,key):
        indices={'inicio':7,'laboratorio':0,'modelos':4,'particulas':5,'resultados':3,'cuaderno':6}
        if key not in indices:return
        index=self.tabs.currentIndex() if key=='laboratorio' and self.tabs.currentIndex() in {0,1,2} else indices[key]
        self.tabs.setCurrentIndex(index);self._section_from_tab(index)

    def _section_from_tab(self,index):
        key={3:'resultados',4:'modelos',5:'particulas',6:'cuaderno',7:'inicio'}.get(index,'laboratorio')
        self.active_section=key
        for name,button in self.nav_buttons.items():button.setChecked(name==key)
        lab=key=='laboratorio';context=key in {'laboratorio','resultados'}
        self.sidebar.setVisible(lab);self.tabs.tabBar().setVisible(lab)
        for widget in [self.workspace_eyebrow,self.experiment_label,*self.metrics]:widget.setVisible(context)
        self.workspace_title.setVisible(False)
        self.state_label.setVisible(context);self.csv_button.setVisible(context)
        if lab:self.content_splitter.setSizes([320,1100])

    def open_example(self,key):
        if self.worker is not None:
            self.statusBar().showMessage('Espera a que termine el cálculo para cargar otro ejemplo.',6000);return
        self.apply_config(example_config(key))
        self.example_selector.setCurrentIndex(self.example_selector.findData(key))
        self.run_simulation()

    def open_family(self,family):
        self.navigate_section('modelos')
        self.library_family_selector.setCurrentIndex(self.library_family_selector.findData(family))

    def _build_library(self):
        page=QWidget();layout=QVBoxLayout(page)
        title=QLabel('Biblioteca de modelos y ejemplos');title.setObjectName('title');layout.addWidget(title)
        detail=QLabel('Consulta los supuestos, las unidades y los resultados esperados antes de abrir un experimento.');detail.setObjectName('muted');detail.setWordWrap(True);layout.addWidget(detail)
        filters=QHBoxLayout();self.library_family_selector=QComboBox();self.library_family_selector.addItem('Todas las áreas','')
        for family in dict.fromkeys(spec.family for spec in MODELS.values()):self.library_family_selector.addItem(family,family)
        self.library_model_selector=QComboBox()
        for key,spec in MODELS.items():self.library_model_selector.addItem(spec.name,key)
        filters.addWidget(self.library_family_selector);filters.addWidget(self.library_model_selector,1);layout.addLayout(filters)
        row=QHBoxLayout();self.library_example_selector=QComboBox();row.addWidget(self.library_example_selector,1)
        button=QPushButton('Abrir ejemplo en el laboratorio');button.clicked.connect(lambda:self.open_example(self.library_example_selector.currentData()));row.addWidget(button);layout.addLayout(row)
        self.guide=GuidePanel();layout.addWidget(self.guide,1)
        self.library_family_selector.currentIndexChanged.connect(self._library_filter_changed)
        self.library_model_selector.currentIndexChanged.connect(self._library_model_changed)
        self.library_example_selector.currentIndexChanged.connect(self._library_example_changed)
        return page

    def _library_filter_changed(self,*_):
        previous=self.library_model_selector.currentData();family=self.library_family_selector.currentData()
        self.library_model_selector.blockSignals(True);self.library_model_selector.clear()
        for key,spec in MODELS.items():
            if not family or spec.family==family:self.library_model_selector.addItem(spec.name,key)
        self.library_model_selector.setCurrentIndex(max(0,self.library_model_selector.findData(previous)))
        self.library_model_selector.blockSignals(False);self._library_model_changed()

    def _library_model_changed(self,*_):
        key=self.library_model_selector.currentData()
        if key is None:return
        self.library_example_selector.blockSignals(True);self.library_example_selector.clear()
        for example in EXAMPLES:
            if example.model==key:self.library_example_selector.addItem(example.label,example.key)
        self.library_example_selector.blockSignals(False);self._library_example_changed()

    def _library_example_changed(self,*_):
        key=self.library_model_selector.currentData()
        if key:self.guide.set_model(key,self.library_example_selector.currentData())

    def _sync_library(self,model,example=None):
        if self.library_model_selector.findData(model)<0:
            self.library_family_selector.blockSignals(True);self.library_family_selector.setCurrentIndex(0);self.library_family_selector.blockSignals(False)
            self._library_filter_changed()
        self.library_model_selector.blockSignals(True);self.library_model_selector.setCurrentIndex(self.library_model_selector.findData(model));self.library_model_selector.blockSignals(False)
        self._library_model_changed()
        if example:self.library_example_selector.setCurrentIndex(self.library_example_selector.findData(example))

    def _build_header(self):
        header = NeoSurface(); header.setObjectName('header')
        box = QHBoxLayout(header); box.setContentsMargins(10, 14, 10, 14)
        brand = QLabel('DYNAMIS'); brand.setObjectName('brand')
        box.addWidget(brand)
        subtitle = QLabel('LABORATORIO DE FÍSICA · EDICIÓN 2\nMecánica · Caos · Partículas · Cuántica'); subtitle.setObjectName('muted')
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
        outer = NeoSurface(); outer.setObjectName('sidebar'); outer.setMinimumWidth(290); outer.setMaximumWidth(410)
        box = QVBoxLayout(outer); box.setContentsMargins(10, 12, 10, 10)
        eyebrow = QLabel('01 / CONFIGURAR EXPERIMENTO'); eyebrow.setObjectName('eyebrow'); box.addWidget(eyebrow)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        body = QWidget(); self.side_layout = QVBoxLayout(body); self.side_layout.setContentsMargins(2, 0, 2, 0)
        self.family_selector = QComboBox(); self.family_selector.addItem('Todas las áreas', '')
        for family in dict.fromkeys(spec.family for spec in MODELS.values()):
            self.family_selector.addItem(family, family)
        self.family_selector.currentIndexChanged.connect(self._filter_models)
        self.side_layout.addWidget(self.family_selector)
        self.model_selector = QComboBox()
        self.model_selector.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.model_selector.setMinimumContentsLength(17)
        for key, name in MODEL_NAMES.items():
            self.model_selector.addItem(name, key)
        self.model_selector.currentIndexChanged.connect(self._model_changed)
        self.side_layout.addWidget(self.model_selector)
        self.model_summary = QLabel(); self.model_summary.setObjectName('muted'); self.model_summary.setWordWrap(True)
        self.side_layout.addWidget(self.model_summary)
        self.example_selector = QComboBox(); self.example_selector.currentIndexChanged.connect(self._example_changed)
        self.example_selector.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.example_selector.setMinimumContentsLength(17)
        self.side_layout.addWidget(self.example_selector)
        self.load_example_button = QPushButton('Cargar ejemplo y simular')
        self.load_example_button.clicked.connect(self.load_example); self.side_layout.addWidget(self.load_example_button)
        self.time_group, general = self._group('Tiempo')
        self.time_form = general
        general.addRow('Duración T', self._number('duration', 25., .5, 120., step=1))
        self.time_help = QLabel(); self.time_help.setObjectName('muted'); self.time_help.setWordWrap(True)
        general.addRow(self.time_help)
        self.physical_group, self.physical_form = self._group('Parámetros físicos · SI')
        self.physical_form.addRow('Masa m (kg)', self._number('mass', 1., .05, 100.))
        self.physical_form.addRow('Rigidez k (N/m)', self._number('stiffness', 4., .05, 100.))
        self.physical_form.addRow('Amortig. c (kg/s)', self._number('damping', .2, 0., 30.))
        self.lorenz_group, form = self._group('Parámetros de Lorenz')
        for key, label, val, low, high in [('sigma', 'σ', 10., .1, 50.), ('rho', 'ρ', 28., 0., 100.),
                                           ('beta', 'β', 8/3, .1, 10.)]:
            form.addRow(label, self._number(key, val, low, high, decimals=6))
        form.addRow('Perturbación Δx', self._number('delta', .0001, 1e-8, 1., decimals=8, step=.0001))
        self.initial_group, self.initial_form = self._group('Condiciones iniciales')
        for key, label, val in [('x0', 'x₀ (m)', 1.), ('v0', 'v₀ (m/s)', 0.), ('y0', 'y₀', 1.), ('z0', 'z₀', 1.)]:
            self.initial_form.addRow(label, self._number(key, val, -100., 100., decimals=6))
        self.ensemble_group, form = self._group('Conjunto probabilístico')
        form.addRow('Desv. k (N/m)', self._number('stiffness_std', .4, 0., 10.))
        form.addRow('Desv. x₀ (m)', self._number('position_std', .05, 0., 10.))
        form.addRow('Realizaciones N', self._number('count', 1000, 100, 10000, step=100, integer=True))
        form.addRow('Umbral a (m)', self._number('threshold', .5, -100., 100.))
        note = QLabel('K y X₀ uniformes e independientes.\nEste conjunto usa c = 0.'); note.setObjectName('muted'); note.setWordWrap(True); form.addRow(note)
        self.dynamic_group, self.dynamic_form = self._group('Campos del modelo')
        self.dynamic_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.seed_group, form = self._group('Reproducibilidad')
        form.addRow('Semilla', self._number('seed', 42, 0, 2147483647, step=1, integer=True))
        self.solver_group, self.solver_form = self._group('Precisión y muestreo')
        self.solver_form.addRow('Tolerancia rtol', self._number('rtol', 1e-9, 1e-12, 1e-3, step=1e-9))
        self.solver_form.addRow('Tolerancia atol', self._number('atol', 1e-11, 1e-14, 1e-3, step=1e-11))
        self.solver_form.addRow('Paso máximo', self._number('max_step', .05, .001, 2., decimals=3, step=.01))
        self.solver_form.addRow('Puntos de salida', self._number('points', 1200, 200, 3000, step=100, integer=True))
        self.side_layout.addStretch()
        scroll.setWidget(body); box.addWidget(scroll, 1)
        self.run_button = QPushButton('Simular experimento'); self.run_button.setObjectName('primary')
        self.run_button.clicked.connect(self.run_simulation); box.addWidget(self.run_button)
        return outer

    def _build_workspace(self):
        area = Workspace(); box = QVBoxLayout(area); box.setContentsMargins(10, 0, 0, 0); box.setSpacing(9)
        eyebrow = QLabel('LABORATORIO / OBSERVAR · MEDIR · CONTRASTAR'); eyebrow.setObjectName('eyebrow'); box.addWidget(eyebrow); self.workspace_eyebrow=eyebrow
        title = QLabel('Explora el movimiento.'); title.setObjectName('title'); box.addWidget(title); self.workspace_title=title
        self.experiment_label = QLabel('Configura un experimento y pulsa Simular.'); self.experiment_label.setObjectName('muted')
        self.experiment_label.setTextFormat(Qt.TextFormat.PlainText); self.experiment_label.setWordWrap(True); box.addWidget(self.experiment_label)
        cards = QHBoxLayout(); cards.setSpacing(9); self.metrics = [Metric() for _ in range(4)]
        for card in self.metrics:
            cards.addWidget(card)
        box.addLayout(cards)
        self.tabs = QTabWidget(); self.tabs.setTabBar(NeoTabBar())
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
        self.time_label = QLabel('t = 0'); self.time_label.setObjectName('numeric'); self.time_label.setMinimumWidth(120); timeline.addWidget(self.time_label)
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
        self.data_panel = DatasetPanel(); self.tabs.addTab(self.data_panel, 'Datos')
        self.tabs.addTab(self._build_library(), 'Guía y ejemplos')
        self.particle_panel = ParticlePanel(); self.tabs.addTab(self.particle_panel, 'Partículas')
        notebook = QWidget(); notebook_box = QVBoxLayout(notebook)
        metadata_form = QFormLayout(); self.metadata_fields = {}
        for key, label in [('project_name','Nombre del proyecto'),('researcher','Investigador/a'),('objective','Objetivo / hipótesis'),('references','Fuentes propias')]:
            field = QLineEdit(); field.setMaxLength(10000)
            if key == 'project_name':field.setText('Experimento sin título')
            self.metadata_fields[key] = field; metadata_form.addRow(label,field)
        notebook_box.addLayout(metadata_form)
        notebook_box.addWidget(QLabel('Hipótesis, supuestos, fuentes y observaciones'))
        self.notes = QTextEdit(); self.notes.setPlaceholderText('Pregunta de investigación:\n\nHipótesis:\n\nSupuestos del modelo:\n\nFuentes / referencias:\n\nObservaciones y próximos experimentos:')
        notebook_box.addWidget(self.notes, 1)
        note = QLabel('Las notas se guardan junto con parámetros, tolerancias y semilla en el proyecto JSON.'); note.setWordWrap(True); note.setObjectName('muted'); notebook_box.addWidget(note)
        self.tabs.addTab(notebook, 'Cuaderno')
        self.dashboard=Dashboard();self.dashboard.exampleRequested.connect(self.open_example);self.dashboard.familyRequested.connect(self.open_family)
        self.tabs.addTab(self.dashboard,'Inicio')
        for index in range(3,self.tabs.count()):self.tabs.setTabVisible(index,False)
        self.tabs.currentChanged.connect(self._section_from_tab)
        box.addWidget(self.tabs, 1)
        footer = QHBoxLayout()
        self.state_label = QLabel('Preparado'); self.state_label.setObjectName('status'); footer.addWidget(self.state_label, 1)
        self.csv_button = QPushButton('Exportar CSV + configuración'); self.csv_button.setEnabled(False); self.csv_button.clicked.connect(self.export_csv); footer.addWidget(self.csv_button)
        box.addLayout(footer)
        return area

    def _filter_models(self, *_):
        previous = self.model_selector.currentData()
        family = self.family_selector.currentData()
        self.model_selector.blockSignals(True); self.model_selector.clear()
        for key,spec in MODELS.items():
            if not family or spec.family == family:self.model_selector.addItem(spec.name,key)
        index = self.model_selector.findData(previous)
        self.model_selector.setCurrentIndex(max(0,index)); self.model_selector.blockSignals(False)
        if not self.loading:self._model_changed()

    def _configure_model(self, model, *, rebuild=True):
        spec = MODELS[model]; legacy = model in {'oscillator','lorenz','ensemble'}
        self.physical_group.setVisible(model in {'oscillator','ensemble'})
        self.physical_form.setRowVisible(self.fields['damping'], model == 'oscillator')
        self.lorenz_group.setVisible(model == 'lorenz')
        self.ensemble_group.setVisible(model == 'ensemble')
        self.initial_group.setVisible(legacy)
        self.initial_form.setRowVisible(self.fields['v0'], model != 'lorenz')
        self.initial_form.setRowVisible(self.fields['y0'], model == 'lorenz')
        self.initial_form.setRowVisible(self.fields['z0'], model == 'lorenz')
        self.initial_form.labelForField(self.fields['x0']).setText('x₀' if model == 'lorenz' else 'x₀ (m)')
        self.time_group.setVisible(spec.timed)
        self.fields['duration'].setRange(*(spec.time_range if spec.timed else (1e-12,1e10)))
        self.time_form.labelForField(self.fields['duration']).setText('Duración ('+spec.time_unit+')')
        self.time_help.setText('Tiempo de evolución en '+spec.time_unit+'.' if spec.timed else '')
        self.model_summary.setText(spec.summary)
        self.seed_group.setVisible(model in {'ensemble','radioactive'})
        self.dynamic_group.setVisible(not legacy)
        self.solver_group.setVisible(model != 'logistic')
        for key in ['rtol','atol','max_step']:
            self.solver_form.setRowVisible(self.fields[key], spec.numeric)
        self.solver_form.labelForField(self.fields['points']).setText('Puntos espaciales' if model == 'quantum_barrier' else 'Puntos de salida')
        self.fields['max_step'].setToolTip('Paso del reloj interno: segundos en modelos SI, adimensional en Lorenz/Duffing, τ normalizado en órbitas y campos E/B. Consulta Fórmulas y precisión.')
        if rebuild:
            self.dynamic_fields = {}
            while self.dynamic_form.rowCount():
                self.dynamic_form.removeRow(0)
            # El área desplazable debe crecer en vertical: las etiquetas van
            # encima de su entrada y nunca se comprimen al añadir muchos campos.
            self.dynamic_group.setMinimumHeight(45+70*len(spec.parameters))
            for parameter in spec.parameters:
                if parameter.choices:
                    widget = QComboBox()
                    for key,label in parameter.choices:widget.addItem(label,key)
                    widget.setCurrentIndex(widget.findData(parameter.default));widget.currentIndexChanged.connect(self._mark_dirty)
                else:
                    widget = QSpinBox() if parameter.integer else ScientificNumber()
                    if not parameter.integer:widget.setDecimals(20)
                    widget.setRange(parameter.low,parameter.high);widget.setSingleStep(parameter.step);widget.setValue(parameter.default)
                    widget.setKeyboardTracking(False);widget.valueChanged.connect(self._mark_dirty)
                detail = parameter.description
                if not parameter.choices:detail += f' · Rango: {parameter.low:g} a {parameter.high:g}'
                widget.setToolTip(detail);widget.setMinimumWidth(95)
                widget.setMinimumHeight(30)
                label = QLabel(parameter.caption);label.setWordWrap(True);label.setToolTip(detail);label.setMinimumHeight(20)
                self.dynamic_form.addRow(label,widget);self.dynamic_fields[parameter.key]=widget

    def _refresh_examples(self):
        previous=self.example_selector.currentData()
        self.example_selector.blockSignals(True);self.example_selector.clear()
        for example in EXAMPLES:
            if example.model==self.model_selector.currentData():self.example_selector.addItem(example.label,example.key)
        found=self.example_selector.findData(previous)
        self.example_selector.setCurrentIndex(max(0,found));self.example_selector.blockSignals(False)
        self._example_changed()

    def _example_changed(self,*_):
        model=self.model_selector.currentData()
        if model and hasattr(self,'guide'):self._sync_library(model,self.example_selector.currentData())

    def _model_changed(self, *_):
        if self.loading or self.model_selector.currentData() is None:return
        model=self.model_selector.currentData();changed=model!=self._last_model
        self._configure_model(model,rebuild=changed)
        if changed:self.fields['duration'].setValue(MODELS[model].duration)
        self._last_model=model;self._refresh_examples()
        self._mark_dirty()

    def load_example(self):
        if self.worker is not None:return
        key=self.example_selector.currentData()
        if key is None:return
        self.apply_config(example_config(key))
        self.example_selector.setCurrentIndex(self.example_selector.findData(key))
        self.run_simulation()

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
                                  notes=self.notes.toPlainText(),
                                  parameters={k:(w.currentData() if isinstance(w,QComboBox) else w.value()) for k,w in self.dynamic_fields.items()},
                                  **{k:w.text() for k,w in self.metadata_fields.items()}, **values)
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
        self.scene_note.setText(descriptions.get(model,MODELS[model].scene_note)+' Arrastra para girar; usa las herramientas para acercar.')
        self.experiment_label.setText(MODEL_NAMES[model]+' · '+str(len(result.t))+' puntos · '+result.config.project_name[:100])
        self.experiment_label.setToolTip(result.config.project_name)
        self.state_label.setText('Resultados actualizados · DOP853 y comparación de refinamiento' if MODELS[model].numeric
                                 else 'Resultados actualizados · consulta los supuestos y diagnósticos del modelo')
        self.data_panel.set_result(result)
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
        if 'metrics' in e:
            values=e['metrics']
        elif c.model == 'oscillator':
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
        if 'diagnostic' in e:
            body=e['diagnostic']
        elif c.model == 'ensemble':
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
        self.precision_text.setHtml('<div style="color:#c4d2e7; line-height:1.5">'+body+'</div>')

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
            model=self.result.config.model
            value=self.result.t[index]
            if model=='quantum_barrier':text=f'x = {value:.5g} nm'
            elif model=='logistic':text=f'n = {index}'
            elif model in {'em_particle','two_body'}:text=f't = {value*1e9:.5g} ns'
            elif model in {'lorenz','duffing'}:text=f't = {value:.5g}'
            else:text=f't = {value:.5g} s'
            self.time_label.setText(text)

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
        self.family_selector.setCurrentIndex(0)
        self._filter_models()
        self.model_selector.setCurrentIndex(self.model_selector.findData(config.model))
        self._configure_model(config.model,rebuild=True)
        for key, widget in self.fields.items():
            if hasattr(config, key):
                widget.setValue(getattr(config, key))
        self.fields['rtol'].setValue(config.solver.rtol)
        self.fields['atol'].setValue(config.solver.atol)
        self.fields['max_step'].setValue(config.solver.max_step)
        self.fields['points'].setValue(config.solver.points)
        for key,value in MODELS[config.model].values(config.parameters).items():
            widget=self.dynamic_fields[key]
            if isinstance(widget,QComboBox):widget.setCurrentIndex(widget.findData(value))
            else:widget.setValue(value)
        for key,widget in self.metadata_fields.items():widget.setText(getattr(config,key))
        self.notes.setPlainText(config.notes)
        self._last_model=config.model
        self.loading = False
        self._refresh_examples();self._mark_dirty();self.navigate_section('laboratorio')

    def export_csv(self):
        if self.result is None or self.dirty or self.worker is not None:
            self.state_label.setText('Simula los parámetros actuales antes de exportar.'); return
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar resultados', 'resultados.csv', 'Datos CSV (*.csv)')
        if not path:
            return
        try:
            frame=self.data_panel.current_frame()
            if frame is None:frame=self.result.dataframe()
            frame.to_csv(path, index=False, float_format='%.17g')
            self.result.config.notes = self.notes.toPlainText()
            for key,widget in self.metadata_fields.items():setattr(self.result.config,key,widget.text())
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
                canvas = self.analysis if self.tabs.currentIndex() == 1 else self.formulas if self.tabs.currentIndex() == 2 else self.scene
                canvas.figure.savefig(path, dpi=220, facecolor=canvas.figure.get_facecolor())
                self.statusBar().showMessage('Figura exportada: '+path, 8000)
            except OSError as error:
                QMessageBox.warning(self, 'No se pudo exportar', str(error))

    def closeEvent(self, event):
        if self.worker is not None:
            self.state_label.setText('El cálculo está terminando. Podrás cerrar la ventana al finalizar.'); event.ignore()
        else:
            self.timer.stop(); event.accept()
