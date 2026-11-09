"""Inicio del laboratorio: áreas de trabajo y experimentos destacados."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout,QHBoxLayout,QLabel,QScrollArea,QVBoxLayout,QWidget
from catalog import MODELS,EXAMPLES
from particle_data import PARTICLES
from theme import NeoSurface,NeoButton,LatexNumber


class Dashboard(QWidget):
    exampleRequested=Signal(str)
    familyRequested=Signal(str)

    def __init__(self):
        super().__init__()
        outer=QVBoxLayout(self);outer.setContentsMargins(0,0,0,0)
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        body=QWidget();box=QVBoxLayout(body);box.setContentsMargins(12,12,12,12);box.setSpacing(15)
        hero=NeoSurface();hero_box=QVBoxLayout(hero);hero_box.setContentsMargins(25,23,25,23)
        tag=QLabel('DYNAMIS 2 / ESPACIO CIENTÍFICO');tag.setObjectName('eyebrow');hero_box.addWidget(tag)
        title=QLabel('Una pregunta. Muchas formas de explorar.');title.setObjectName('homeTitle');title.setWordWrap(True);hero_box.addWidget(title)
        subtitle=QLabel('Modela, observa y contrasta. Elige un experimento, ajusta sus parámetros y conserva cada resultado en tu cuaderno.');subtitle.setObjectName('muted');subtitle.setWordWrap(True);hero_box.addWidget(subtitle)
        box.addWidget(hero)
        stats=QHBoxLayout();stats.setSpacing(13)
        for value,label in [(len(MODELS),'Modelos para explorar'),(len(EXAMPLES),'Ejemplos guiados'),(len(PARTICLES),'Especies en el catálogo'),(sum(len(x.parameters) for x in MODELS.values()),'Campos específicos de modelo')]:
            frame=NeoSurface();frame_box=QVBoxLayout(frame);frame_box.setContentsMargins(20,13,20,15)
            number=LatexNumber(str(value));frame_box.addWidget(number)
            text=QLabel(label);text.setObjectName('muted');frame_box.addWidget(text);stats.addWidget(frame)
        box.addLayout(stats)
        heading=QLabel('Áreas de estudio');heading.setObjectName('cardTitle');box.addWidget(heading)
        families=QGridLayout();families.setSpacing(10)
        for i,family in enumerate(dict.fromkeys(x.family for x in MODELS.values())):
            button=NeoButton(family);button.clicked.connect(lambda checked=False,key=family:self.familyRequested.emit(key));families.addWidget(button,i//3,i%3)
        box.addLayout(families)
        heading=QLabel('Experimentos destacados');heading.setObjectName('cardTitle');box.addWidget(heading)
        grid=QGridLayout();grid.setSpacing(13)
        highlights=[('gas_dilute','Un gas en movimiento','Esferas, choques elásticos, energía y presión en 3D.'),
                    ('gravity_disk','Partículas que interactúan','Fuerzas mutuas, conservación y comparación de pasos.'),
                    ('rossler_classic','Explorar sistemas dinámicos','Atractores, condiciones vecinas y barridos de parámetros.'),
                    ('kuramoto_sync','Sincronización colectiva','Fases acopladas y parámetro de orden de Kuramoto.'),
                    ('orbit_circle','Órbita circular','Geometría orbital, energía y momento angular.'),
                    ('electron_helix','Hélice de un electrón','Movimiento relativista en un campo magnético.'),
                    ('pion_boost','Un pión y dos productos','Cinemática de decaimiento y conservación del cuatro-momento.'),
                    ('quantum_tunnel','Al otro lado de la barrera','Función de onda, reflexión y transmisión cuántica.')]
        for i,(key,title,description) in enumerate(highlights):
            example=next(x for x in EXAMPLES if x.key==key)
            frame=NeoSurface();card=QVBoxLayout(frame);card.setContentsMargins(22,18,22,17);card.setSpacing(7)
            family=QLabel(MODELS[example.model].family.upper());family.setObjectName('eyebrow');card.addWidget(family)
            label=QLabel(title);label.setObjectName('cardTitle');card.addWidget(label)
            detail=QLabel(description);detail.setObjectName('muted');detail.setWordWrap(True);card.addWidget(detail)
            button=NeoButton('Explorar ejemplo');button.clicked.connect(lambda checked=False,name=key:self.exampleRequested.emit(name));card.addWidget(button)
            grid.addWidget(frame,i//2,i%2)
        box.addLayout(grid)
        hint=QLabel('Partículas 3D: gas y fuerzas mutuas · Dinámica: sistemas y barridos · Modelos: ecuaciones y ejemplos · Catálogo: propiedades · Resultados: datos · Cuaderno: tu investigación')
        hint.setObjectName('muted');hint.setWordWrap(True);box.addWidget(hint)
        box.addStretch();scroll.setWidget(body);outer.addWidget(scroll)
