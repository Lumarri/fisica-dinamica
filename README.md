# Física y sistemas dinámicos

Laboratorio interactivo en español para explorar física, dinámica no lineal e incertidumbre. Primera versión funcional, orientada a experimentos reproducibles.

## Abrir en VS Code

Necesitas VS Code, Git y Python 3.11 o posterior en tu computadora.

1. En VS Code pulsa **F1**, ejecuta **Git: Clone** (Git: Clonar) y pega `https://github.com/Lumarri/fisica-dinamica.git`.
2. Elige una carpeta y abre el repositorio clonado. Instala las extensiones recomendadas de Python, Pylance y Python Debugger cuando el editor las ofrezca.
3. Pulsa **F1** y ejecuta **Python: Create Environment**. Elige **Venv**, un Python 3.11 o posterior y `requirements.txt` para instalar las dependencias.
4. Pulsa **F5** y selecciona **Física: ejecutar interfaz**. Abre la dirección local que aparece en la terminal, normalmente `http://localhost:8501`.

Si ya tienes un entorno, usa **Python: Select Interpreter** y selecciona el Python de `.venv`. La configuración incluida permite descubrir las pruebas en el panel **Testing**. Para detener la aplicación, detén la depuración.

Para subir tus cambios a GitHub, inicia sesión cuando VS Code lo solicite, crea un commit en **Control de código fuente** y usa **Sincronizar cambios**. La primera clonación establece la conexión del repositorio con GitHub.

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
