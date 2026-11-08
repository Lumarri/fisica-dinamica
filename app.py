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
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    window = MainWindow(auto_run=False)
    window.show()
    report = {'status': 'failed', 'models': []}
    try:
        for model in ['oscillator', 'lorenz', 'ensemble']:
            config = ExperimentConfig(model=model, duration=4, count=100,
                                      solver=SolverSettings(points=300))
            window.apply_config(config)
            window.accept_result(run_experiment(config))
            for canvas in [window.scene, window.analysis, window.formulas]:
                canvas.draw()
            app.processEvents()
            if not window.grab().save(str(directory / f'{model}.png')):
                raise RuntimeError('No se pudo guardar la captura de verificación.')
            report['models'].append(model)
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
