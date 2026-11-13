"""Tema neumórfico nativo: superficies de doble sombra y controles con relieve."""
from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPalette, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QPushButton, QTabBar, QStyle, QSlider, QLabel
from PySide6.QtGui import QFontDatabase, QIcon
from pathlib import Path
import re
from io import BytesIO

BASE = '#18253a'
TEXT = '#e6eef9'
MUTED = '#a7b8cf'
ACCENT = '#87c7fa'
BLUE = '#6899ef'
SHADOW = '#0b1423'
LIGHT = '#2e4262'

STYLE = """
QWidget { color:#e6eef9; font-family:'Space Grotesk','Segoe UI','DejaVu Sans'; font-size:12px; background:transparent; }
QMainWindow, QWidget#root, QDialog { background:#18253a; }
QFrame#header, QFrame#sidebar, QFrame#metric { border:none; background:transparent; }
QLabel#brand { font-size:24px; font-weight:700; color:#87c7fa; }
QLabel#eyebrow { color:#87c7fa; font-size:10px; font-weight:700; }
QLabel#title { font-size:24px; font-weight:600; color:#e6eef9; }
QLabel#muted { color:#a7b8cf; font-size:11px; }
QLabel#metricvalue { color:#edf4ff; font-family:cmr10; font-size:26px; }
QLabel#metriclabel { color:#a7b8cf; font-size:10px; }
QLabel#numeric { color:#dce9fa; font-family:cmr10; font-size:16px; }
QLabel#homeTitle { color:#eef5ff; font-size:30px; font-weight:600; }
QLabel#cardTitle { color:#dceaff; font-size:17px; font-weight:600; }
QLabel#status { color:#a7b8cf; padding:5px; }
QGroupBox {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #203149,stop:1 #17273e);
    border-top:1px solid #2e4262; border-left:1px solid #2e4262;
    border-bottom:1px solid #101c2e; border-right:1px solid #101c2e;
    border-radius:13px; margin-top:17px; padding:14px 10px 10px; font-weight:600;
}
QGroupBox::title { subcontrol-origin:margin; left:13px; color:#b7c8e1; padding:0 4px; }
QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #111e32,stop:.6 #192a43,stop:1 #213650);
    border-top:1px solid #0c1625; border-left:1px solid #0c1625;
    border-bottom:1px solid #2e4262; border-right:1px solid #2e4262;
    border-radius:9px; padding:7px 9px; min-height:18px; color:#e6eef9;
    selection-background-color:#2a4b70; selection-color:#e4efff;
}
QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus, QLineEdit:focus { border:1px solid #6b9bcd; }
QAbstractSpinBox { font-family:cmr10; font-size:16px; }
QAbstractSpinBox QLineEdit { background:transparent; border:none; padding:0; min-height:0; font-family:cmr10; font-size:16px; }
QSpinBox::up-button,QDoubleSpinBox::up-button { subcontrol-origin:padding; subcontrol-position:top right; width:19px; border:none; background:transparent; }
QSpinBox::down-button,QDoubleSpinBox::down-button { subcontrol-origin:padding; subcontrol-position:bottom right; width:19px; border:none; background:transparent; }
QComboBox::drop-down { width:22px; border:none; }
QComboBox QAbstractItemView { background:#203149; color:#e6eef9; border:1px solid #304966; selection-background-color:#2a4b70; }
QPushButton { background:transparent; border:none; padding:10px 16px; min-height:23px; }
QPushButton#primary { font-weight:700; min-height:27px; }
QPushButton:disabled { color:#657b98; }
QTabWidget::pane {
    background:#18253a; border-top:1px solid #0f1a2c; border-left:1px solid #0f1a2c;
    border-bottom:1px solid #2e4262; border-right:1px solid #2e4262; border-radius:17px;
}
QTabBar { background:transparent; }
QTextEdit, QTextBrowser {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #14233a,stop:1 #1d304c);
    border-top:1px solid #0d182a; border-left:1px solid #0d182a;
    border-bottom:1px solid #2e4262; border-right:1px solid #2e4262;
    border-radius:12px; padding:12px; color:#40536b; selection-background-color:#2a4b70;
}
QScrollArea { border:none; background:transparent; }
QScrollArea > QWidget > QWidget { background:transparent; }
QScrollBar:vertical { width:10px; background:#111e32; border-radius:5px; margin:2px; }
QScrollBar::handle:vertical { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #304969,stop:1 #304968); border:1px solid #233d5c; min-height:28px; border-radius:4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QScrollBar:horizontal { height:10px; background:#111e32; border-radius:5px; }
QScrollBar::handle:horizontal { background:#304968; min-width:28px; border-radius:4px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width:0; }
QSlider::groove:horizontal { height:7px; background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #0b1525,stop:1 #304a6b); border-radius:4px; }
QSlider::handle:horizontal { width:19px; height:19px; margin:-7px 0; border:2px solid #304968; border-radius:11px; background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #304968,stop:.5 #1b2f4b,stop:1 #294a6d); }
QSlider::handle:horizontal:hover { border-color:#87c7fa; }
QCheckBox::indicator { width:16px; height:16px; border-radius:5px; border-top:1px solid #0b1423; border-left:1px solid #0b1423; border-bottom:1px solid #304969; border-right:1px solid #304969; background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #101e32,stop:1 #233a58); }
QCheckBox { color:#b7c8e1; spacing:8px; }
QToolBar { border:none; background:transparent; padding:3px; spacing:5px; }
QToolButton { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #253d5c,stop:1 #14253c); padding:5px; border-top:1px solid #2e4262; border-left:1px solid #2e4262; border-bottom:1px solid #101c2e; border-right:1px solid #101c2e; border-radius:7px; }
QToolButton:pressed, QToolButton:checked { background:#13243c; border-color:#43658d; }
QMenuBar { background:#18253a; color:#b7c8e1; }
QMenu { background:#203149; border:1px solid #2e4564; padding:7px; }
QMenu::item { padding:7px 20px; border-radius:6px; }
QMenu::item:selected { background:#2b4c72; color:#b7dfff; }
QStatusBar { color:#a7b8cf; background:#18253a; }
QToolTip { color:#e6eef9; background:#253951; border:1px solid #2e4262; padding:8px; }
QHeaderView::section { color:#b7c8e1; background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #2b4361,stop:1 #1a2d46); padding:9px; border-top:1px solid #2e4262; border-left:1px solid #2e4262; border-bottom:1px solid #0e1a2c; border-right:1px solid #0e1a2c; }
"""


def surface(painter, rect, radius=14, *, inset=False, active=False, strength=1.):
    """Sombras claras arriba/izquierda, oscuras abajo/derecha; sin filtros de imagen."""
    painter.save();painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    rect=QRectF(rect)
    face=QLinearGradient(rect.topLeft(),rect.bottomRight())
    face.setColorAt(0,QColor('#2a4669' if active else '#22344f'))
    face.setColorAt(1,QColor('#1d3454' if active else '#16243a'))
    if not inset:
        painter.setPen(Qt.PenStyle.NoPen)
        for layer in range(10,0,-1):
            spread=layer*.35;offset=2.5+layer*.18
            expanded=rect.adjusted(-spread,-spread,spread,spread)
            shade=QColor(SHADOW);shade.setAlpha(int((5+10*(1-layer/11))*strength))
            painter.setBrush(shade);painter.drawRoundedRect(expanded.translated(offset,offset),radius+spread,radius+spread)
            shine=QColor(LIGHT);shine.setAlpha(int((7+13*(1-layer/11))*strength))
            painter.setBrush(shine);painter.drawRoundedRect(expanded.translated(-offset,-offset),radius+spread,radius+spread)
        painter.setBrush(face);painter.drawRoundedRect(rect,radius,radius)
        painter.setBrush(Qt.BrushStyle.NoBrush);painter.setPen(QPen(QColor('#304969'),.8))
        painter.drawRoundedRect(rect.adjusted(.5,.5,-.5,-.5),radius,radius)
    else:
        face.setColorAt(0,QColor('#12263e' if active else '#111e32'))
        face.setColorAt(1,QColor('#223c5b' if active else '#1b2e49'))
        painter.setPen(Qt.PenStyle.NoPen);painter.setBrush(face);painter.drawRoundedRect(rect,radius,radius)
        path=QPainterPath();path.addRoundedRect(rect,radius,radius);painter.setClipPath(path)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for layer in range(8,0,-1):
            shade=QColor(SHADOW);shade.setAlpha(int(5+9*(1-layer/9)))
            shine=QColor(LIGHT);shine.setAlpha(int(9+11*(1-layer/9)))
            painter.setPen(QPen(shade,layer*1.5));painter.drawRoundedRect(rect.translated(2.2,2.2),radius,radius)
            painter.setPen(QPen(shine,layer*1.5));painter.drawRoundedRect(rect.translated(-2.2,-2.2),radius,radius)
    painter.restore()


class NeoSurface(QFrame):
    """Superficie estática con caché adaptada a pantallas de alta densidad."""
    def __init__(self,parent=None):
        super().__init__(parent);self._background=None;self._cache_key=None

    def paintEvent(self,event):
        ratio=self.devicePixelRatioF();key=(self.width(),self.height(),ratio)
        if self._cache_key!=key:
            image=QPixmap(max(1,int(self.width()*ratio)),max(1,int(self.height()*ratio)))
            image.setDevicePixelRatio(ratio);image.fill(Qt.GlobalColor.transparent)
            painter=QPainter(image)
            surface(painter,QRectF(7,7,max(1,self.width()-14),max(1,self.height()-14)),17)
            painter.end();self._background=image;self._cache_key=key
        painter=QPainter(self);painter.drawPixmap(0,0,self._background)


class NeoButton(QPushButton):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.setCursor(Qt.CursorShape.PointingHandCursor)

    def sizeHint(self):
        base=super().sizeHint();return QSize(base.width()+4,max(43,base.height()))

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        active=self.objectName()=='primary';pressed=self.isDown() or self.isChecked()
        rect=QRectF(self.rect()).adjusted(6,6,-6,-6)
        surface(p,rect,11,inset=pressed,active=active,strength=1.1 if self.underMouse() else .85)
        color=ACCENT if active or self.isChecked() else TEXT
        p.setPen(QColor(color if self.isEnabled() else '#657b98'))
        font=self.font();font.setBold(active);p.setFont(font)
        padding=5 if self.property('compact') else 9
        p.drawText(rect.adjusted(padding,0,-padding,0),Qt.AlignmentFlag.AlignCenter,self.text())
        if self.hasFocus():
            p.setBrush(Qt.BrushStyle.NoBrush);p.setPen(QPen(QColor('#759dcd'),1))
            p.drawRoundedRect(rect.adjusted(2,2,-2,-2),9,9)

    def enterEvent(self,event):
        self.update();super().enterEvent(event)

    def leaveEvent(self,event):
        self.update();super().leaveEvent(event)


class NeoTabBar(QTabBar):
    def __init__(self,parent=None):
        super().__init__(parent);self.setDrawBase(False);self.setExpanding(False)

    def tabSizeHint(self,index):
        return QSize(self.fontMetrics().horizontalAdvance(self.tabText(index))+30,45)

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for index in range(self.count()):
            rect=QRectF(self.tabRect(index)).adjusted(5,5,-5,-5)
            selected=index==self.currentIndex()
            surface(p,rect,10,inset=selected,active=selected,strength=.65)
            p.setPen(QColor(ACCENT if selected else MUTED))
            font=self.font();font.setBold(selected);p.setFont(font)
            p.drawText(rect,Qt.AlignmentFlag.AlignCenter,self.tabText(index))


def setup_style(app):
    load_fonts()
    app.setStyle('Fusion');palette=QPalette()
    roles={QPalette.ColorRole.Window:BASE,QPalette.ColorRole.WindowText:TEXT,
           QPalette.ColorRole.Base:'#14243b',QPalette.ColorRole.AlternateBase:'#203149',
           QPalette.ColorRole.Text:TEXT,QPalette.ColorRole.Button:BASE,
           QPalette.ColorRole.ButtonText:TEXT,QPalette.ColorRole.Highlight:'#2b4e76',
           QPalette.ColorRole.HighlightedText:'#e9f3ff',QPalette.ColorRole.ToolTipBase:'#22364f',
           QPalette.ColorRole.ToolTipText:TEXT,QPalette.ColorRole.PlaceholderText:'#889fbd'}
    for role,color in roles.items():palette.setColor(role,QColor(color))
    app.setPalette(palette);app.setFont(QFont('Space Grotesk',10))
    root=Path(__file__).resolve().parent/'assets'/'ui'
    arrows='QSpinBox::up-arrow,QDoubleSpinBox::up-arrow { image:url(\"'+(root/'chevron-up.svg').as_posix()+'\"); width:10px; height:8px; } QComboBox::down-arrow,QSpinBox::down-arrow,QDoubleSpinBox::down-arrow { image:url(\"'+(root/'chevron-down.svg').as_posix()+'\"); width:10px; height:8px; }'
    checked='QCheckBox::indicator:checked { image:url(\"'+(root/'check.svg').as_posix()+'\"); }'
    app.setStyleSheet(STYLE+arrows+checked)


_fonts_ready=False


def load_fonts():
    global _fonts_ready
    if _fonts_ready:return
    from matplotlib import get_data_path,rcParams
    font=Path(__file__).resolve().parent/'assets'/'fonts'/'SpaceGrotesk.ttf'
    if font.is_file():QFontDatabase.addApplicationFont(str(font))
    for name in ['cmr10.ttf','cmb10.ttf','cmmi10.ttf']:
        path=Path(get_data_path())/'fonts'/'ttf'/name
        if path.is_file():QFontDatabase.addApplicationFont(str(path))
    rcParams.update({'mathtext.fontset':'cm','axes.formatter.use_mathtext':True,'axes.unicode_minus':False})
    _fonts_ready=True


class NeoSlider(QSlider):
    def sizeHint(self):
        hint=super().sizeHint();return QSize(hint.width(),max(30,hint.height()))

    def paintEvent(self,event):
        if self.orientation()!=Qt.Orientation.Horizontal:return super().paintEvent(event)
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        width=max(1,self.width()-28);cy=self.height()/2
        surface(p,QRectF(14,cy-3,width,6),3,inset=True)
        fraction=(self.value()-self.minimum())/max(1,self.maximum()-self.minimum())
        if self.invertedAppearance():fraction=1-fraction
        cx=14+width*fraction
        surface(p,QRectF(cx-8,cy-8,16,16),8,active=self.isSliderDown())
        p.setBrush(QColor(ACCENT));p.setPen(Qt.PenStyle.NoPen);p.drawEllipse(QRectF(cx-2.4,cy-2.4,4.8,4.8))

    def _value_at(self,event):
        return QStyle.sliderValueFromPosition(self.minimum(),self.maximum(),int(event.position().x()-14),max(1,self.width()-28),self.invertedAppearance())

    def mousePressEvent(self,event):
        if self.orientation()==Qt.Orientation.Horizontal and event.button()==Qt.MouseButton.LeftButton:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            self.setSliderDown(True);self.setValue(self._value_at(event));self.update();event.accept()
        else:super().mousePressEvent(event)

    def mouseMoveEvent(self,event):
        if self.orientation()==Qt.Orientation.Horizontal and self.isSliderDown():self.setValue(self._value_at(event));self.update();event.accept()
        else:super().mouseMoveEvent(event)

    def mouseReleaseEvent(self,event):
        if self.orientation()==Qt.Orientation.Horizontal and self.isSliderDown():self.setSliderDown(False);self.update();event.accept()
        else:super().mouseReleaseEvent(event)


class LatexNumber(QLabel):
    """Lectura estática en Computer Modern, con notación científica de LaTeX."""
    def __init__(self,text='',parent=None):
        super().__init__(parent);self._math=None;self.setMinimumHeight(34);self.setText(text)

    def setText(self,text):
        super().setText(str(text));self.setAccessibleName(str(text));self.setToolTip(str(text));self._math=None
        value=str(text).replace('−','-').replace('∞',r'\infty')
        if ' – ' in value:
            a,b=value.split(' – ',1);value=r'\left['+a+','+b+r'\right]'
        value=re.sub(r'(-?\d+(?:\.\d+)?)e([+-]?\d+)',lambda m:m[1]+r'\times 10^{'+str(int(m[2]))+'}',value)
        value=value.replace('%',r'\%').replace('—',r'\cdots')
        try:
            from matplotlib.mathtext import math_to_image
            from matplotlib.font_manager import FontProperties
            from matplotlib import rc_context
            data=BytesIO()
            with rc_context({'savefig.transparent':True}):
                math_to_image('$'+value+'$',data,prop=FontProperties(size=18),dpi=160,format='png',color=TEXT)
            pixmap=QPixmap();pixmap.loadFromData(data.getvalue());self._math=pixmap
        except (ValueError,RuntimeError):pass
        self.update()

    def sizeHint(self):return QSize(80,38)

    def minimumSizeHint(self):return QSize(45,34)

    def paintEvent(self,event):
        if self._math is None or self._math.isNull():return super().paintEvent(event)
        p=QPainter(self)
        image=self._math.scaled(max(1,self.width()-4),max(1,self.height()-6),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        p.drawPixmap(2,int((self.height()-image.height())/2),image)
