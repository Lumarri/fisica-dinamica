# DYNAMIS 2 · Laboratorio de física de escritorio

Programa nativo para **Windows x64**, con **30 modelos**, **68 ejemplos guiados** y un catálogo de **28 especies de partículas**. Incluye mecánica, dinámica no lineal, probabilidades, electromagnetismo relativista y modelos introductorios de física de partículas y cuántica. La interfaz usa Qt y Matplotlib y trabaja localmente.

## Descargar y ejecutar en Windows

**Descarga directa:** [última versión para Windows x64](https://github.com/Lumarri/fisica-dinamica/releases/latest). Descarga `Dynamis.exe` y ábrelo; no requiere instalar Python.

También se conservan los paquetes de verificación de cada compilación:

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

## Diseño y secciones

Tema **neumórfico oscuro en azul marino**, con superficies de doble sombra, controles hundidos y estados activos en azul hielo. **Space Grotesk** se incluye para la interfaz; **Computer Modern**, la tipografía clásica de LaTeX, se usa en fórmulas, lecturas científicas, entradas numéricas y datos. No hace falta instalar fuentes ni una distribución de TeX para usar el programa.

La navegación principal ofrece **Inicio, Laboratorio, Partículas 3D, Dinámica, Geo / Grafos, Modelos, Catálogo, Resultados y Cuaderno**. Inicio abre experimentos destacados; la biblioteca permite filtrar por área, consultar supuestos y cargar ejemplos. El área de trabajo es desplazable en ventanas pequeñas.

La fuente Space Grotesk se distribuye bajo SIL Open Font License 1.1; se conserva su licencia en `assets/fonts/OFL.txt`.

## Modelos incluidos

| Área | Modelos | Campos y resultados destacados |
| --- | --- | --- |
| Mecánica | Oscilador amortiguado, péndulo no lineal, proyectil 3D, órbita gravitatoria y osciladores acoplados | Masas, longitudes, rigideces, fricción, gravedad, viento vectorial, arrastre, excentricidad e inclinación; energías, impacto y momento angular |
| Caos y dinámica | Lorenz, péndulo doble, Duffing, mapa logístico, Rössler, Van der Pol, Lotka–Volterra, SIR, Hénon y Kuramoto | Condiciones iniciales, perturbaciones, forzamiento, transitorios y barridos; espacio de estados, sección estroboscópica, FFT, bifurcaciones y Lyapunov del mapa |
| Simuladores de partículas | Gas de esferas elásticas y N cuerpos con gravedad o cargas | Cantidad, geometría, radio, masa, velocidad, fuerza, suavizado y paso; colisiones, presión, energía, momentos, trayectorias completas y convergencia |
| Probabilidades | Conjunto de osciladores | Realizaciones, semilla, incertidumbre de rigidez y posición, percentiles, distribución conjunta e intervalo Wilson |
| Partículas y cuántica | Partícula relativista en E/B, Rutherford, población radiactiva, decaimiento de dos cuerpos y barrera cuántica 1D | Especie, energía, campos vectoriales, impacto, carga del blanco, semivida, eficiencia, fondo, masas de productos, boost y barrera; trayectorias, secciones eficaces, cuentas, cuatro-momentos y transmisión/reflexión |

Consulta la [guía detallada de modelos, parámetros y ejemplos](docs/MODELOS.md). La misma información se encuentra dentro del programa en **Modelos y ejemplos**.

## Nuevos simuladores y sistemas dinámicos

- **Partículas 3D → Gas de esferas elásticas:** hasta 96 esferas, recipiente cúbico, masas/radios iguales, semilla, rapidez RMS y paso configurables. Incluye presión por impulso en paredes, conteo de choques y balance de energía/momento con el recipiente. El tamaño de los puntos es ilustrativo; el radio físico se usa en los contactos.
- **Partículas 3D → N cuerpos:** hasta 128 partículas con gravedad o cargas de signos alternos, nube o disco, rotación y dispersión inicial. Usa potencial suavizado y Velocity Verlet; compara con la mitad del paso. Trabaja en unidades reducidas declaradas: uL, uM, uT y uE = uM·uL²/uT².
- **Dinámica:** incorpora Rössler, Van der Pol, Lotka–Volterra, SIR, Hénon y Kuramoto. Cada modelo nuevo compara condiciones vecinas y barre un parámetro con mínimo, máximo y número de valores elegibles. Van der Pol, Lotka–Volterra y SIR muestran campos de direcciones normalizados en el plano de estados.
- **Reproducción:** pausa, volver al inicio, fotograma anterior/siguiente, velocidad y repetición. Se anima una simulación ya calculada. Kuramoto representa fases en el círculo unitario.
- **Resultados:** elige **Trayectorias de partículas**, **Propiedades iniciales** o **Barrido de parámetros** cuando estén disponibles. CSV incluye todas las filas y la configuración reproducible del experimento.

Los barridos nuevos comienzan cada valor desde el mismo estado y semilla; muestran extremos a tiempo finito, no bifurcaciones demostradas. Los escapes se registran con NaN y estado. Los modelos clásicos de muchas partículas complementan los módulos relativistas/cuánticos existentes.

## Geometría, grafos y nuevos escenarios 3D · versión 2.2

La sección **Geo / Grafos** abre la geometría y las redes. La biblioteca permite filtrar **Geometría 3D** y **Grafos y redes**. Los nuevos escenarios de partículas aparecen en **Partículas 3D**.

| Escenario | Qué permite investigar |
| --- | --- |
| Compton 3D | Energía y ángulos del fotón, retroceso del electrón, cuatro-momento y sección diferencial Klein–Nishina |
| Trampa de Paul | Confinamiento RF, micromovimiento y trabajo de una fuente cuadrupolar en unidades reducidas |
| Superficies paramétricas | Esfera, toro, Möbius y paraboloide; malla triangulada, área y refinamiento |
| Geodésicas esféricas | Latitud, longitud, rumbo, arco recorrido y cuerda |
| Grafos y rutas | Mundo pequeño, Erdős–Rényi, retícula y grafo geométrico; grados, componentes, agrupamiento y Dijkstra |
| Difusión en grafos | Laplaciano, conservación de cantidad y equilibrio por componente, con color animado |
| Red de osciladores | Modos normales, desplazamientos, energía y amortiguamiento sobre una red |

Los controles **Malla / red** y **Nodos** muestran u ocultan la geometría y las etiquetas. La escala de color permanece fija durante la reproducción. Los CSV adicionales incluyen aristas/pesos, matrices, rutas, límites de equilibrio y modos normales según el escenario. Origen se cuenta desde 1; destino 0 selecciona el último nodo.

Compton parte de un electrón libre en reposo; su curva angular es sección eficaz, no probabilidad normalizada. La trampa de Paul usa Mathieu ideal, sin electrodos ni carga espacial. Las superficies son geometría estática y el cursor no representa tiempo físico. La difusión usa cantidades abstractas con capacidad unitaria. La red vibratoria es un modelo escalar sobre un grafo; las aristas no son resortes centrales con longitud natural geométrica.

## Primer experimento

1. Abre **Laboratorio** o elige un experimento destacado en **Inicio**. Selecciona el área y el modelo que quieres estudiar.
2. Elige un ejemplo y pulsa **Cargar ejemplo y simular**. El proyecto incluye una descripción del resultado esperado.
3. Consulta **Escena 3D**, **Series y estadística** y **Fórmulas y precisión** dentro de Laboratorio. Las tablas y exportaciones están en **Resultados**.
4. Modifica un parámetro, vuelve a simular y contrasta la hipótesis.
5. En **Cuaderno**, registra proyecto, investigador/a, objetivo, fuentes y observaciones. Guarda el proyecto JSON y exporta los datos o figuras.

Ejemplos para comenzar: tiro parabólico en vacío, órbita circular, transferencia entre osciladores, Lorenz estable/caótico, hélice de electrón y positrón, alfa sobre oro, población de muones en reposo, `π⁺ → μ⁺ν`, `K⁺ → π⁺π⁰`, `Z⁰ → e⁺e⁻` y túnel bajo una barrera.

Los [68 proyectos JSON de ejemplo](examples/) también se incluyen en el repositorio. El ejecutable lleva los ejemplos integrados y no necesita esos archivos externos.

## Escenas, datos y proyectos

- **3D:** giro con el ratón, acercamiento, planos XY/XZ/YZ, múltiples partículas animadas y controles de reproducción. Péndulos con varillas animadas y decaimiento de dos cuerpos con ambas trayectorias.
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
- **Muchas partículas:** el gas usa impulsos elásticos con detección de contacto por subpasos y corrección de penetración; los tiempos de choque son aproximados. El modelo N cuerpos usa Verlet y potencial suavizado; ε cambia el potencial y no representa el error numérico. Ambos subdividen los intervalos de salida respetando Δt máximo.
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

La interfaz utiliza PySide6/Qt 6.11.3, validado con Python 3.11. El iniciador de Windows actualiza esa dependencia si detecta otra versión.

Se verifican choques elásticos, impulso con paredes, fuerzas como gradiente del potencial, convergencia de Verlet, conservación de momentos, Van der Pol armónico, equilibrio/integral de Lotka–Volterra, población SIR, mapa de Hénon y fases libres de Kuramoto. También se verifican soluciones e invariantes físicos: oscilación armónica, disipación, péndulos, tiro en vacío, período kepleriano, modos acoplados, campo eléctrico y magnético, energía de Rutherford, ley de semivida, cuatro-momento relativista y `R+T=1` en la barrera. Se contrastan además conservación relativista en Compton, movimiento libre en Paul, áreas analíticas, costura de Möbius, geodésicas, rutas, difusión y energía modal. También se prueban ejemplos, persistencia, compatibilidad de proyectos, tablas, exportaciones y los dibujos/fórmulas de los 30 modelos.

El flujo de Windows construye el `.exe` y ejecuta la aplicación empaquetada con los 30 modelos, comprobando Qt, cálculos, figuras y capturas en modo `offscreen`. Guarda `verification.json`, capturas y versiones de dependencias en el artefacto.

## Estructura

| Archivo | Función |
| --- | --- |
| `app.py` | Arranque y verificación del ejecutable |
| `desktop.py`, `panels.py`, `dashboard.py` | Secciones, ventana, formularios, inicio, datos y guías |
| `theme.py`, `assets/` | Neumorfismo oscuro, fuentes e iconos |
| `catalog.py` | Definiciones de campos, unidades, supuestos, fórmulas y ejemplos |
| `models.py` | Integrador y modelos originales |
| `advanced_models.py` | Mecánica adicional, caos, partículas y barrera cuántica |
| `particle_simulator.py` | Gas elástico y N cuerpos con fuerzas mutuas |
| `dynamic_systems.py` | Sistemas ampliados, condiciones vecinas, campos y barridos |
| `spatial_models.py`, `graph_models.py` | Compton, Paul, geometría y dinámica de grafos |
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
