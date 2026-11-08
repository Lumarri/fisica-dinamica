# PyInstaller: ejecutable nativo autocontenido (compilar en Windows).
a = Analysis(
    ['app.py'], pathex=[], binaries=[], datas=[],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['streamlit', 'plotly', 'PyQt5', 'PyQt6', 'PySide2', 'tkinter'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='Dynamis', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, console=False,
)
