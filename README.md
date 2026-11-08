# DYNAMIS 2 · Laboratorio de física de escritorio

Programa nativo para **Windows x64**, con **15 modelos**, **34 ejemplos guiados** y un catálogo de **28 especies de partículas**. Incluye mecánica, dinámica no lineal, probabilidades, electromagnetismo relativista y modelos introductorios de física de partículas y cuántica. La interfaz usa Qt y Matplotlib y trabaja localmente.

## Descargar y ejecutar en Windows

1. Abre [Build Windows desktop](https://github.com/Lumarri/fisica-dinamica/actions/workflows/windows.yml).
2. Entra en la compilación más reciente que haya terminado correctamente.
3. Descarga **Dynamis-Windows-x64**, extrae el ZIP y abre `dist/Dynamis.exe`.

El ejecutable empaquetado incluye Python y las bibliotecas necesarias. El artefacto conserva también capturas e informe de verificación. Las descargas de Actions requieren iniciar sesión en GitHub y caducan a los 14 días. El ejecutable es para Windows x64 y no incluye firma de código.

### Desde VS Code o el código fuente

Requiere Git, Python **3.11 o posterior** y, para editar, VS Code con las extensiones recomendadas. Clona `https://github.com/Lumarri/fisica-dinamica.git` con **F1 → Git: Clone**. En la terminal, dentro del repositorio:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

También puedes abrir `Iniciar_Dynamis.bat`, que prepara el entorno e instala las dependencias que faltan. La primera instalación necesita Internet. Para depurar, elige el intérprete de `.venv` con **Python: Select Interpreter** y pulsa **F5**.

Si ya tienes el repositorio, actualízalo con `git pull` e instala de nuevo `requirements.txt` en tu entorno. En Linux/macOS también se puede ejecutar el código con `python app.py`; Ubuntu/Debian necesita `libegl1` y `libopengl0` para Qt. El flujo de empaquetado genera el ejecutable de Windows.

## Modelos incluidos

| Área | Modelos | Campos y resultados destacados |
| --- | --- | --- |
| Mecánica | Oscilador amortiguado, péndulo no lineal, proyectil 3D, órbita gravitatoria y osciladores acoplados | Masas, longitudes, rigideces, fricción, gravedad, viento vectorial, arrastre, excentricidad e inclinación; energías, impacto y momento angular |
| Caos y dinámica | Lorenz, péndulo doble, Duffing y mapa logístico | Condiciones iniciales, perturbaciones, forzamiento, transitorios y barridos; espacio de estados, sección estroboscópica, FFT, bifurcaciones y Lyapunov del mapa |
| Probabilidades | Conjunto de osciladores | Realizaciones, semilla, incertidumbre de rigidez y posición, percentiles, distribución conjunta e intervalo Wilson |
| Partículas y cuántica | Partícula relativista en E/B, Rutherford, población radiactiva, decaimiento de dos cuerpos y barrera cuántica 1D | Especie, energía, campos vectoriales, impacto, carga del blanco, semivida, eficiencia, fondo, masas de productos, boost y barrera; trayectorias, secciones eficaces, cuentas, cuatro-momentos y transmisión/reflexión |

Consulta la [guía detallada de modelos, parámetros y ejemplos](docs/MODELOS.md). La misma información se encuentra dentro del programa en **Guía y ejemplos**.

## Primer experimento

1. Selecciona un área y un modelo en la barra lateral.
2. Elige un ejemplo y pulsa **Cargar ejemplo y simular**. El proyecto incluye una descripción del resultado esperado.
3. Consulta **Escena 3D**, **Series y estadística**, **Fórmulas y precisión** y **Datos**.
4. Modifica un parámetro, vuelve a simular y contrasta la hipótesis.
5. En **Cuaderno**, registra proyecto, investigador/a, objetivo, fuentes y observaciones. Guarda el proyecto JSON y exporta los datos o figuras.

Ejemplos para comenzar: tiro parabólico en vacío, órbita circular, transferencia entre osciladores, Lorenz estable/caótico, hélice de electrón y positrón, alfa sobre oro, población de muones en reposo, `π⁺ → μ⁺ν`, `K⁺ → π⁺π⁰`, `Z⁰ → e⁺e⁻` y túnel bajo una barrera.

Los [34 proyectos JSON de ejemplo](examples/) también se incluyen en el repositorio. El ejecutable lleva los ejemplos integrados y no necesita esos archivos externos.

## Escenas, datos y proyectos

- **3D:** giro con el ratón, acercamiento, planos XY/XZ/YZ y reproducción del cursor. Péndulos con varillas animadas y decaimiento de dos cuerpos con ambas trayectorias.
- **Coordenadas explícitas:** una escena puede ser espacial, de estados o compleja. Los rótulos indican qué significa cada eje. La función de onda cuántica no se representa como trayectoria de una partícula.
- **Fórmulas:** ecuaciones renderizadas en la ventana y diagnósticos del método utilizado.
- **Datos:** tabla de hasta 1000 filas visibles, selección de conjuntos auxiliares y copia con Ctrl+C. Exportar CSV guarda **todas** las filas del conjunto seleccionado con 17 cifras significativas de float64.
- **Proyectos:** esquema JSON v2 con modelo, parámetros completos, semilla, tolerancias y metadatos de investigación. Se siguen abriendo proyectos v1.
- **Exportación:** CSV y `.experiment.json` asociado; figuras 3D, series o fórmulas en PNG a 220 dpi. La selección del conjunto se refleja en las columnas del CSV; el JSON conserva la configuración del experimento.
- Cambiar parámetros desactiva la exportación y reproducción de resultados anteriores hasta volver a simular. Los cambios de notas y metadatos se incorporan al guardar/exportar.

Las simulaciones se ejecutan en segundo plano. Mientras se calcula, el programa permite consultar las pestañas. El cierre espera a que termine el cálculo.

## Precisión, unidades y alcance

- Aritmética **float64**. Las cifras mostradas o exportadas no garantizan igual cantidad de decimales físicamente correctos.
- Los modelos diferenciales usan **DOP853** y se comparan con una integración con `rtol/10`, `atol/10` y `paso/2`. Se normaliza cada componente por `max(1, max|referencia|)`. Es un diagnóstico empírico, no una cota garantizada del error global.
- Cada modelo declara sus unidades. La duración orbital se introduce en períodos; internamente se integra con `τ = t√(GM/a³)`. En campos E/B se normalizan tiempo, posición y momento para resolver las distintas escalas. El panel de precisión detalla el reloj interno del paso máximo.
- Más puntos de salida aumentan la resolución de las figuras; no sustituyen tolerancias adecuadas. La FFT tiene resolución finita y la sección de Poincaré de Duffing usa interpolación lineal.
- Las bandas de percentiles, los intervalos de confianza de una probabilidad y los cuantiles de población tienen significados diferentes; las leyendas y guías lo especifican.
- El catálogo de partículas distingue especies elementales y compuestas. Sus masas son valores nominales de referencia; las incertidumbres no están tabuladas. Las masas de quarks dependen del esquema y escala; las de los estados de sabor de neutrinos no se fijan en esta tabla.
- Los módulos de partículas calculan los procesos descritos. No incorporan un generador de colisiones de teoría cuántica de campos, todos los canales de decaimiento, hadronización, detectores completos ni todas las especies hadrónicas. Los supuestos concretos de cada módulo aparecen en su guía.
- Los ejemplos con neutrino usan masa nula como aproximación cinemática; Rutherford trata el blanco como puntual y fijo; la barrera usa Schrödinger estacionario 1D no relativista.

## Construir el ejecutable

En Windows, dentro del repositorio y con `.venv` creado:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean Dynamis.spec
```

El resultado es `dist\Dynamis.exe`. También puedes ejecutar `scripts/build_windows.ps1`. La compilación debe realizarse en Windows; un binario generado en Linux no es un `.exe` de Windows.

## Validación

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Se verifican soluciones e invariantes físicos: oscilación armónica, disipación, péndulos, tiro en vacío, período kepleriano, modos acoplados, campo eléctrico y magnético, energía de Rutherford, ley de semivida, cuatro-momento relativista y `R+T=1` en la barrera. También se prueban ejemplos, persistencia, compatibilidad de proyectos, tablas, exportaciones y los dibujos/fórmulas de los 15 modelos.

El flujo de Windows construye el `.exe` y ejecuta la aplicación empaquetada con los 15 modelos, comprobando Qt, cálculos, figuras y capturas en modo `offscreen`. Guarda `verification.json`, capturas y versiones de dependencias en el artefacto.

## Estructura

| Archivo | Función |
| --- | --- |
| `app.py` | Arranque y verificación del ejecutable |
| `desktop.py`, `panels.py` | Ventana, formularios, datos, guía y catálogo de partículas |
| `catalog.py` | Definiciones de campos, unidades, supuestos, fórmulas y ejemplos |
| `models.py` | Integrador y modelos originales |
| `advanced_models.py` | Mecánica adicional, caos, partículas y barrera cuántica |
| `particle_data.py` | Propiedades de referencia y conversiones de unidades |
| `experiments.py` | Configuración validada, persistencia y resultados |
| `plotting.py` | Escenas 3D, análisis y fórmulas |
| `examples/`, `docs/` | Proyectos de ejemplo y guía de estudio |

## Referencias de base

- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html).
- [OpenStax · University Physics, volúmenes 1–3](https://openstax.org/subjects/science).
- [Particle Data Group](https://pdg.lbl.gov/).
- [NIST · CODATA](https://physics.nist.gov/cuu/Constants/).
- [Lorenz (1963), Deterministic Nonperiodic Flow](https://doi.org/10.1175/1520-0469(1963)020%3C0130:DNF%3E2.0.CO;2).
- [Wilson (1927), Probable Inference, the Law of Succession, and Statistical Inference](https://doi.org/10.1080/01621459.1927.10502953).
