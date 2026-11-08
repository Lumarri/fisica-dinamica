# DYNAMIS · Física y sistemas dinámicos

Aplicación **nativa de escritorio para Windows**, escrita en Python, Qt y Matplotlib. Se abre en una ventana propia y funciona localmente después de instalar las dependencias. Esta versión sustituye la interfaz inicial de Streamlit.

## Usar el programa en Windows

### Ejecutable

En [Actions → Build Windows desktop](https://github.com/Lumarri/fisica-dinamica/actions/workflows/windows.yml), abre la compilación correcta más reciente y descarga el artefacto **Dynamis-Windows-x64**. Extrae el ZIP y abre `dist/Dynamis.exe`. Los artefactos caducan a los 14 días; también puedes compilarlos localmente. No se necesita Python para el ejecutable empaquetado. La compilación es para Windows x64 y no incluye firma de código.

La compilación verifica los modelos, dibuja las figuras de la aplicación empaquetada y conserva capturas y un informe en `build-smoke/` dentro del artefacto. Una compilación fallida no proporciona un ejecutable verificado.

### Desde el código y VS Code

Necesitas Git, VS Code y Python **3.11 o posterior**. Clona el repositorio con **F1 → Git: Clone** y esta dirección:

```text
https://github.com/Lumarri/fisica-dinamica.git
```

Instala las extensiones recomendadas. En una terminal de VS Code, dentro del repositorio:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

También puedes abrir `Iniciar_Dynamis.bat`: crea el entorno si hace falta e instala las dependencias que faltan. La primera instalación necesita Internet.

Para depurar, selecciona el intérprete de `.venv` con **Python: Select Interpreter** y pulsa **F5 → Dynamis: programa de escritorio**. Si ya tenías la versión anterior, actualiza el repositorio e instala de nuevo `requirements.txt` en tu entorno.

Linux y macOS también pueden ejecutar el código con un entorno virtual y `python app.py`; el ejecutable incluido en el flujo de compilación es específico de Windows.

## Qué puedes estudiar

- **Oscilador amortiguado:** masa, rigidez, amortiguamiento, posición y velocidad iniciales. Energía y disipación en unidades SI.
- **Lorenz:** parámetros σ, ρ y β, condiciones iniciales y perturbación en x. Trayectoria vecina y separación de estados.
- **Conjunto probabilístico:** rigidez y posición inicial aleatorias, uniformes e independientes; masa y velocidad inicial fijas, sin amortiguamiento. Semilla reproducible, percentiles, distribución conjunta de posición y velocidad finales, y probabilidad de superar un umbral.

### Planos 3D

La escena permite giro con el ratón, herramientas de acercamiento, vistas **XY / XZ / YZ**, planos de referencia y reproducción del marcador temporal. Las curvas representan la trayectoria completa; el marcador indica el instante seleccionado.

En el oscilador y el conjunto, los ejes son **posición, velocidad y tiempo**: es un espacio de fases ampliado, no una trayectoria espacial en tres dimensiones. En Lorenz, los ejes son las tres variables adimensionales del estado. En el conjunto se muestran hasta 24 realizaciones y la trayectoria de parámetros nominales.

### Fórmulas visibles

Las ecuaciones se renderizan dentro de la ventana, en **Fórmulas y precisión**.

Oscilador:

$$m\ddot{x}+c\dot{x}+kx=0,\qquad E=\tfrac12 mv^2+\tfrac12 kx^2,\qquad \frac{dE}{dt}=-cv^2.$$

Lorenz:

$$\dot{x}=\sigma(y-x),\qquad \dot{y}=x(\rho-z)-y,\qquad \dot{z}=xy-\beta z.$$

Conjunto, con $\omega=\sqrt{K/m}$:

$$x(t)=X_0\cos(\omega t)+\frac{v_0}{\omega}\sin(\omega t),\qquad \hat p=\frac1N\sum_i \mathbf{1}[x_i(T)>a].$$

## Precisión y significado de los resultados

- **Aritmética:** float64; no se promete exactitud arbitraria ni una cantidad garantizada de decimales correctos.
- **Integración:** DOP853 con tolerancia relativa, tolerancia absoluta y paso máximo ajustables. La escala de control local es `atol + rtol·|y|`.
- **Comparación de refinamiento:** una segunda integración usa `rtol/10`, `atol/10` y `paso/2`. Se muestran las diferencias máximas por variable y una diferencia normalizada. Cada componente se divide por `max(1, máximo absoluto de la referencia)`. Es un diagnóstico empírico, no una cota garantizada del error global.
- **Referencia analítica:** para el oscilador con amortiguamiento cero también se compara la posición con su solución analítica.
- **Caos:** a tiempos largos, Lorenz puede separar soluciones calculadas con tolerancias distintas. Esto limita la predicción de trayectorias individuales.
- **Muestreo temporal:** controla la resolución de las figuras y los valores exportados. Más puntos de salida no equivalen a un integrador más preciso; los picos mostrados son picos muestreados.
- **Monte Carlo:** usa una solución analítica evaluada en coma flotante. Las tolerancias del integrador no intervienen. El intervalo de Wilson del 95 % cuantifica incertidumbre de muestreo de la probabilidad; su cobertura es aproximada y no mide incertidumbre sobre los supuestos físicos. Cero éxitos observados no demuestra probabilidad cero.
- **Bandas de percentiles:** describen dispersión de realizaciones, no un intervalo de confianza de la media. Los intervalos de la gráfica de probabilidad se calculan para cada N; no son una banda simultánea para toda la curva.

El modelo de incertidumbre asume independencia entre K y X₀; no incorpora correlaciones, datos experimentales ni incertidumbre en los demás parámetros.

## Proyectos, datos y figuras

- **Guardar / abrir proyecto:** JSON con modelo, parámetros, semilla, tolerancias y notas. Se validan los valores al cargar. Guardar no implica que se hayan recalculado las figuras.
- **Cuaderno:** hipótesis, referencias y observaciones en texto libre.
- **CSV + configuración:** resultados con 17 cifras significativas y un archivo `.experiment.json` con los parámetros que los produjeron. En modelos numéricos se exportan también las diferencias frente a la integración refinada. Para el conjunto, cada fila es una realización con sus parámetros y estado final.
- **PNG:** exporta la escena 3D o, desde la pestaña de series, los cuatro gráficos a 220 dpi.
- Cambiar parámetros desactiva la reproducción y la exportación de los resultados anteriores hasta volver a simular.

Los cálculos se ejecutan en segundo plano. Si intentas cerrar durante una simulación, la ventana espera a que esta termine antes de permitir el cierre.

## Construir tu propio .exe

En Windows, desde la carpeta del repositorio y con el entorno creado:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean Dynamis.spec
```

El resultado es `dist\Dynamis.exe`. Como alternativa, `scripts/build_windows.ps1` ejecuta esos pasos con el entorno `.venv`. PyInstaller debe ejecutarse en el sistema de destino: un ejecutable generado en Linux no sirve como `.exe` de Windows.

## Validación y estructura

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

La suite comprueba soluciones analíticas, disipación y conservación de energía, reproducibilidad, Wilson en casos extremos, persistencia, figuras y fórmulas de los tres modelos, ejecución en segundo plano y exportaciones de la interfaz. Las pruebas de Qt usan su plataforma `offscreen`.

| Archivo | Función |
| --- | --- |
| `app.py` | Inicio de la aplicación y verificación del ejecutable |
| `desktop.py` | Ventana nativa, controles, proyectos y tareas en segundo plano |
| `models.py` | Modelos físicos, integrador y estimación probabilística |
| `experiments.py` | Configuración, resultados y exportación reproducible |
| `plotting.py` | Escenas 3D, series y fórmulas |
| `Dynamis.spec` | Empaquetado con PyInstaller |

## Próximas ampliaciones recomendadas

1. **Péndulo doble y sistemas acoplados:** explorar caos y transferencia de energía con modelos mecánicos adicionales.
2. **Importación de CSV y ajuste de parámetros:** contrastar los modelos con medidas y mostrar residuos e incertidumbre del ajuste.
3. **Bifurcaciones, secciones de Poincaré y exponentes de Lyapunov:** caracterizar regímenes de los sistemas dinámicos.
4. **Análisis de frecuencia FFT y comparación de experimentos:** estudiar resonancias y contrastar escenarios.
5. **Distribuciones correlacionadas e inferencia bayesiana:** ampliar el análisis de conjuntos más allá de uniformes independientes.
6. **Integradores simplécticos:** estudiar conservación de energía a largo plazo en sistemas hamiltonianos.

Estas ampliaciones son propuestas; no forman parte de los modelos implementados en esta versión.

## Referencias

- [SciPy: solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html).
- [OpenStax: oscilaciones amortiguadas](https://openstax.org/books/university-physics-volume-1/pages/15-5-damped-oscillations).
- [Lorenz (1963), Deterministic Nonperiodic Flow](https://doi.org/10.1175/1520-0469(1963)020%3C0130:DNF%3E2.0.CO;2).
- [Wilson (1927), Probable Inference, the Law of Succession, and Statistical Inference](https://doi.org/10.1080/01621459.1927.10502953).
