"""Paneles nativos de consulta, ejemplos y datos."""
import html
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence,QFont
from PySide6.QtWidgets import (QAbstractItemView,QApplication,QComboBox,QHBoxLayout,QLabel,QLineEdit,
                              QTableWidget,QTableWidgetItem,QTextBrowser,QVBoxLayout,QWidget)
from catalog import MODELS, EXAMPLES
from particle_data import PARTICLES


def esc(value):
    return html.escape(str(value))


class CopyTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.number_font=QFont("cmr10",12)
        self.setStyleSheet('QTableWidget { background:#14243b; alternate-background-color:#1b2e48; color:#e2edfc; gridline-color:#2e4767; border-top:1px solid #0c1727; border-left:1px solid #0c1727; border-right:1px solid #2e4565; border-bottom:1px solid #2e4565; border-radius:12px; selection-background-color:#284c75; selection-color:#e6f1ff; }')

    def keyPressEvent(self,event):
        if event.matches(QKeySequence.StandardKey.Copy):
            indices=self.selectedIndexes()
            if not indices:return
            cells={(i.row(),i.column()) for i in indices}
            rows=range(min(i.row() for i in indices),max(i.row() for i in indices)+1)
            cols=range(min(i.column() for i in indices),max(i.column() for i in indices)+1)
            text='\n'.join('\t'.join(self.item(r,c).text() if (r,c) in cells and self.item(r,c) else '' for c in cols) for r in rows)
            QApplication.clipboard().setText(text)
        else:super().keyPressEvent(event)


class DatasetPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.frames={}
        box=QVBoxLayout(self)
        row=QHBoxLayout();row.addWidget(QLabel('Conjunto de datos'))
        self.selector=QComboBox();row.addWidget(self.selector,1);box.addLayout(row)
        self.caption=QLabel('Ejecuta una simulación para consultar sus datos.');self.caption.setWordWrap(True);self.caption.setObjectName('muted');box.addWidget(self.caption)
        self.table=CopyTable();box.addWidget(self.table,1)
        help_label=QLabel('Selecciona celdas y pulsa Ctrl+C. Exportar CSV guarda todas las filas del conjunto seleccionado y su configuración.');help_label.setObjectName('muted');help_label.setWordWrap(True);box.addWidget(help_label)
        self.selector.currentTextChanged.connect(self.refresh)

    def set_result(self,result):
        self.frames={'Resultado principal':result.dataframe(),**result.extra.get('datasets',{})}
        self.selector.blockSignals(True);self.selector.clear();self.selector.addItems(self.frames);self.selector.blockSignals(False)
        self.refresh()

    def current_frame(self):
        return self.frames.get(self.selector.currentText())

    def refresh(self,*_):
        frame=self.current_frame()
        if frame is None:return
        maximum=min(1000,len(frame))
        self.table.setUpdatesEnabled(False)
        self.table.clear();self.table.setRowCount(maximum);self.table.setColumnCount(len(frame.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in frame.columns])
        for row,values in enumerate(frame.head(maximum).itertuples(index=False,name=None)):
            for col,value in enumerate(values):
                text=format(float(value),'.9g') if isinstance(value,(float,np.floating)) else str(value)
                item=QTableWidgetItem(text);item.setToolTip(str(value))
                if isinstance(value,(int,float,np.number)):item.setFont(self.table.number_font)
                self.table.setItem(row,col,item)
        self.table.resizeColumnsToContents();self.table.setUpdatesEnabled(True)
        self.caption.setText(f'{self.selector.currentText()} · {len(frame):,} filas · vista de las primeras {maximum:,}. Las unidades figuran en las columnas. CSV conserva 17 cifras significativas de float64.')


class GuidePanel(QTextBrowser):
    def __init__(self):
        super().__init__();self.setOpenExternalLinks(True)

    def set_model(self,key,example_key=None):
        spec=MODELS[key]
        selected=next((ex for ex in EXAMPLES if ex.key==example_key),None)
        sections=[f'<h2>{esc(spec.name)}</h2><p><b>{esc(spec.family)}</b> · {esc(spec.summary)}</p>']
        if selected:
            sections.append('<h3>Ejemplo seleccionado: '+esc(selected.label)+'</h3><p><b>Qué observar:</b> '+esc(selected.expected)+'</p>')
        sections.append('<h3>Procedimiento</h3><ol><li>Selecciona un ejemplo y pulsa Cargar ejemplo.</li><li>Simula y compara escena, series, fórmulas y diagnósticos.</li><li>Cambia un solo parámetro y comprueba la hipótesis.</li><li>Guarda el proyecto y exporta el conjunto de datos que necesites.</li></ol>')
        sections.append('<h3>Supuestos y alcance</h3><ul>'+''.join('<li>'+esc(x)+'</li>' for x in spec.assumptions)+'</ul>')
        sections.append('<h3>Preguntas para investigar</h3><ul>'+''.join('<li>'+esc(x)+'</li>' for x in spec.questions)+'</ul>')
        if spec.parameters:
            sections.append('<h3>Campos del modelo</h3><table border="1" cellspacing="0" cellpadding="6"><tr><th>Campo</th><th>Unidades</th><th>Rango / opciones</th><th>Detalle</th></tr>')
            for p in spec.parameters:
                domain=', '.join(label for _,label in p.choices) if p.choices else f'{p.low:g} a {p.high:g}'
                sections.append(f'<tr><td>{esc(p.label)}</td><td>{esc(p.unit or "adimensional")}</td><td>{esc(domain)}</td><td>{esc(p.description)}</td></tr>')
            sections.append('</table>')
        sections.append('<h3>Ejemplos incluidos</h3><ul>'+''.join('<li><b>'+esc(ex.label)+'</b>: '+esc(ex.expected)+'</li>' for ex in EXAMPLES if ex.model==key)+'</ul>')
        sections.append('<h3>Referencias</h3><ul>'+''.join(f'<li><a href="{esc(url)}">{esc(label)}</a></li>' for label,url in spec.references)+'</ul>')
        self.setHtml('<div style="color:#c4d2e7;line-height:1.4">'+''.join(sections)+'</div>')


class ParticlePanel(QWidget):
    def __init__(self):
        super().__init__();box=QVBoxLayout(self)
        title=QLabel('Partículas y constantes · catálogo de referencia');title.setObjectName('eyebrow');box.addWidget(title)
        note=QLabel('Masas en MeV/c²; carga en unidades de e; vida media τ en segundos (no semivida). Valores nominales PDG redondeados y constantes CODATA de SciPy; no se tabulan incertidumbres. Las masas de quarks dependen del esquema y escala.');note.setWordWrap(True);note.setObjectName('muted');box.addWidget(note)
        self.search=QLineEdit();self.search.setPlaceholderText('Buscar por nombre, familia, estructura o referencia…');box.addWidget(self.search)
        self.table=CopyTable();box.addWidget(self.table,1)
        refs=QTextBrowser();refs.setMaximumHeight(130);refs.setOpenExternalLinks(True)
        refs.setHtml('<div style="color:#c4d2e7"><b>Unidades y alcance</b><br>1 MeV = 10⁶ eV; 1 fm = 10⁻¹⁵ m; c = 299792458 m/s exactamente en SI. '
            'Las especies de consulta no implican que todos sus procesos estén simulados. Quarks y gluones no se modelan como partículas libres. '
            'Los hadrones y núcleos son compuestos. No se tabulan aquí todos los hadrones ni sus canales.<br>'
            '<a href="https://pdg.lbl.gov/">Particle Data Group</a> · <a href="https://physics.nist.gov/cuu/Constants/">NIST / CODATA</a></div>')
        box.addWidget(refs);self.search.textChanged.connect(self.refresh);self.refresh()

    def refresh(self,*_):
        needle=self.search.text().casefold()
        records=[p for p in PARTICLES.values() if needle in ' '.join([p.name,p.family,p.structure,p.note,p.source]).casefold()]
        self.table.setRowCount(len(records));self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['Partícula','Masa (MeV/c²)','Carga / e','Espín s','Vida media τ (s)','Familia','Estructura','Referencia / detalle'])
        for row,p in enumerate(records):
            lifetime=f'{p.lifetime:.7g}' if p.lifetime is not None else 'Sin decaimiento tabulado'
            if p.family=='Quark' and p.lifetime is None:lifetime='No se asigna aquí'
            spin='1/2' if p.family in {'Leptón','Antileptón','Quark','Barión','Antibarión'} else '1' if p.family=='Bosón gauge' else '0'
            values=[p.name,f'{p.mass_mev:.10g}' if p.mass_mev is not None else 'No fijada por sabor',f'{p.charge_e:.6g}',spin,lifetime,p.family,p.structure,p.source+(' · '+p.note if p.note else '')]
            for col,value in enumerate(values):
                item=QTableWidgetItem(value);item.setToolTip(value)
                if col in {2,3} or (col==1 and p.mass_mev is not None) or (col==4 and p.lifetime is not None):item.setFont(self.table.number_font)
                self.table.setItem(row,col,item)
        self.table.resizeColumnsToContents()
