# Física y sistemas dinámicos

Laboratorio interactivo en español para explorar física, dinámica no lineal e incertidumbre. Primera versión funcional, orientada a experimentos reproducibles.

## Ejecutar

Requiere Python 3.11 o posterior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

En Windows: `.venv\Scripts\activate`.

## Experimentos

- **Oscilador amortiguado:** solución numérica con tolerancias explícitas, posición, espacio de fases y energía en unidades SI.
- **Lorenz:** trayectoria 3D y sensibilidad a una perturbación inicial; variables adimensionales.
- **Monte Carlo:** rigidez uniforme positiva, semilla configurable, percentiles, distribución final y probabilidad de superar un umbral.
- Exportación CSV de los resultados mostrados y JSON de parámetros y notas.

Los modelos están en `models.py`; la interfaz en `app.py`. El oscilador y Lorenz usan `solve_ivp`; Monte Carlo usa la solución analítica del oscilador sin amortiguamiento. Las bandas de percentiles no son intervalos de confianza. No se incorporan fuentes bibliográficas ni datos experimentales automáticamente.

## Validación

```bash
python -m unittest discover -s tests -v
```

## Próximas líneas de investigación

Importación y ajuste de datos experimentales; análisis de bifurcaciones; estimación de parámetros e inferencia bayesiana; registro persistente de experimentos y referencias bibliográficas.
