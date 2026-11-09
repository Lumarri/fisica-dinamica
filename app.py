"""Punto de entrada de la aplicación de escritorio."""
import argparse
import json
from pathlib import Path
import sys
import traceback

from PySide6.QtWidgets import QApplication
from desktop import MainWindow, setup_style


def smoke_test(app, directory):
    """Verifica también el ejecutable empaquetado: Qt, SciPy y las figuras."""
    from experiments import ExperimentConfig, run_experiment
    from models import SolverSettings
    from catalog import MODELS, EXAMPLES
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    window = MainWindow(auto_run=False)
    window.resize(1460,940)
    window.show()
    report = {'status': 'failed', 'models': [], 'examples': len(EXAMPLES), 'edition': '2.1'}
    try:
        from PySide6.QtGui import QFont,QFontInfo
        report['font_families']={'interface':QFontInfo(app.font()).family(),
                                 'numbers':QFontInfo(QFont('cmr10')).family()}
        if not report['font_families']['interface'].startswith('Space Grotesk'):
            raise RuntimeError('La fuente de interfaz no se ha incluido correctamente.')
        if 'cmr10' not in report['font_families']['numbers'].lower():
            raise RuntimeError('La fuente numérica Computer Modern no está disponible.')
        app.processEvents()
        if not window.grab().save(str(directory/'inicio.png')):raise RuntimeError('No se pudo guardar Inicio.')
        for model, spec in MODELS.items():
            config = ExperimentConfig(model=model, duration=min(spec.duration,4), count=100,
                                      solver=SolverSettings(points=300))
            window.apply_config(config)
            window.accept_result(run_experiment(config))
            for canvas in [window.scene, window.analysis, window.formulas]:
                canvas.draw()
            window.timeline.setValue(len(window.result.t)//2)
            app.processEvents()
            if not window.grab().save(str(directory / f'{model}.png')):
                raise RuntimeError('No se pudo guardar la captura de verificación.')
            report['models'].append(model)
        for section in ['simulador','dinamicos','modelos','particulas','resultados','cuaderno']:
            window.navigate_section(section)
            if section in {'simulador','dinamicos'} and window.dirty:
                window.accept_result(run_experiment(window.collect_config()))
                window.timeline.setValue(len(window.result.t)//2)
            app.processEvents()
            if not window.grab().save(str(directory/f'{section}.png')):raise RuntimeError('No se pudo guardar la sección '+section)
        report['sections']=['inicio','laboratorio','simulador','dinamicos','modelos','particulas','resultados','cuaderno']
        report['theme']='Neumorfismo oscuro · azul marino'
        report['typography']=['Space Grotesk','Computer Modern']
        report['status'] = 'passed'
        return 0
    except Exception:
        report['error'] = traceback.format_exc()
        return 1
    finally:
        window.close()
        (directory / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Dynamis · Laboratorio de física de escritorio')
    parser.add_argument('--smoke-test', metavar='DIRECTORIO', help=argparse.SUPPRESS)
    args = parser.parse_args()
    app = QApplication([sys.argv[0]])
    app.setApplicationName('Dynamis')
    app.setOrganizationName('FisicaDinamica')
    setup_style(app)
    if args.smoke_test:
        return smoke_test(app, args.smoke_test)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
