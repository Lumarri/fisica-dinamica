# Guía de modelos y ejemplos · DYNAMIS 2

Esta guía acompaña a las pestañas **Fórmulas y precisión**, **Datos** y **Modelos y ejemplos** del programa.
Incluye 30 modelos y 68 proyectos de ejemplo. El catálogo de referencia contiene 28 especies de partículas.

## Uso de las unidades y de la precisión

Los rangos de cada campo no garantizan que todas sus combinaciones sean válidas. La aplicación comprueba también condiciones conjuntas. Las figuras son espaciales, de estados o complejas según indique cada modelo. En escenas espaciales se aplica la misma escala a los tres ejes.

Las ecuaciones diferenciales ordinarias usan DOP853 y una segunda solución refinada. N cuerpos usa Velocity Verlet y comparación con Δt/2; el gas usa impulsos elásticos aproximados por subpasos. Ambos respetan el paso máximo y subdividen cada intervalo de salida. Las comparaciones de tolerancia no garantizan el error global. Los modelos analíticos conservan las limitaciones de float64 y del muestreo de salida.

Los valores de referencia de partículas son nominales; no incluyen incertidumbres. Consulta PDG o CODATA para un trabajo experimental de precisión. Los quarks tienen masas dependientes del esquema y escala; a los estados de sabor de neutrinos no se les fija aquí una masa.

## 1. Oscilador amortiguado

**Área:** Mecánica.

Movimiento lineal con disipación: posición, velocidad, energía y espacio de fases.

**Escena:** Consulta los rótulos de los ejes: este modelo usa espacio de estados o espacio de fases ampliado.

**Duración:** 25.0 s por defecto; rango 0.5 a 120.

**Campos principales:** m (kg), k (N/m), c (kg/s), x₀ (m), v₀ (m/s), duración (s), tolerancias y paso máximo.

### Supuestos

- Resorte lineal ideal; masa puntual y amortiguamiento viscoso.
- Variables en unidades SI.

### Preguntas para investigar

- ¿Cómo cambia el movimiento entre subamortiguado, crítico y sobreamortiguado?

### Ejemplos

- [Energía conservada](../examples/spring_free.json): La energía permanece constante dentro del error numérico.
- [Amortiguamiento crítico](../examples/spring_critical.json): Con m = 1 y k = 4, c crítico = 4; no hay oscilación.

### Referencias

- [OpenStax · Mecánica](https://openstax.org/details/books/university-physics-volume-1)
- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)

## 2. Atractor de Lorenz

**Área:** Caos y dinámica.

Tres ecuaciones no lineales para investigar sensibilidad a las condiciones iniciales.

**Escena:** Consulta los rótulos de los ejes: este modelo usa espacio de estados o espacio de fases ampliado.

**Duración:** 25.0 adimensional por defecto; rango 0.5 a 120.

**Campos principales:** σ, ρ, β, x₀, y₀, z₀ y perturbación Δx adimensionales; duración y tolerancias.

### Supuestos

- Modelo reducido y adimensional; no es una predicción meteorológica.
- La separación entre dos trayectorias no equivale a un exponente de Lyapunov.

### Preguntas para investigar

- Compara ρ = 10 y ρ = 28; observa los tiempos en los que las trayectorias se separan.

### Ejemplos

- [Lorenz: equilibrio estable](../examples/lorenz_calm.json): Para ρ = 10, las trayectorias tienden a uno de los equilibrios.
- [Lorenz: atractor clásico](../examples/lorenz_chaos.json): Para ρ = 28 aparecen las dos regiones del atractor y sensibilidad inicial.

### Referencias

- [Lorenz (1963)](https://doi.org/10.1175/1520-0469(1963)020%3C0130:DNF%3E2.0.CO;2)

## 3. Conjunto probabilístico

**Área:** Probabilidades.

Realizaciones reproducibles de un oscilador con rigidez y posición inicial inciertas.

**Escena:** Consulta los rótulos de los ejes: este modelo usa espacio de estados o espacio de fases ampliado.

**Duración:** 25.0 s por defecto; rango 0.5 a 120.

**Campos principales:** Masa (kg), rigidez media y desviación (N/m), posición media y desviación (m), v₀ (m/s), umbral (m), N, semilla y duración.

### Supuestos

- K y X₀ son uniformes e independientes; c = 0.
- Percentiles de realizaciones e intervalos de confianza tienen significados distintos.

### Preguntas para investigar

- Mantén la semilla y compara N = 100, 1000 y 10000.
- ¿Qué supuesto de independencia exige tu investigación?

### Ejemplos

- [Incertidumbre pequeña](../examples/ensemble_small.json): Compara la dispersión debida a K y a X₀; son fuentes independientes.
- [Probabilidad con 5000 realizaciones](../examples/ensemble_more.json): El intervalo Wilson cuantifica el error de muestreo; compara con N = 100.

### Referencias

- [Wilson (1927)](https://doi.org/10.1080/01621459.1927.10502953)

## 4. Péndulo no lineal

**Área:** Mecánica.

Péndulo con amortiguamiento y excitación angular. Se compara la dinámica con el régimen de ángulo pequeño.

**Escena:** Posición real del péndulo en el plano XZ; el eje Y es perpendicular al movimiento. La varilla sigue el instante seleccionado.

**Duración:** 25.0 s por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Longitud L | m | 1.0 | 0.05 a 10 | Distancia del pivote a la masa. |
| Masa | kg | 1.0 | 0.01 a 100 | Masa inercial positiva; escala la energía y la respuesta a la fuerza. |
| Gravedad g | m/s² | 9.80665 | 0.01 a 30 | Magnitud constante de la aceleración gravitatoria; actúa hacia −Z. |
| Ángulo inicial | ° | 35.0 | -179 a 179 | Desviación inicial respecto a la vertical inferior; se convierte de grados a radianes. |
| Velocidad angular inicial | rad/s | 0.0 | -20 a 20 | Derivada temporal inicial del ángulo. |
| Amortig. angular | s⁻¹ | 0.03 | 0 a 5 | Coeficiente disipativo; sus unidades dependen de la ecuación del modelo seleccionado. |
| Excitación angular | rad/s² | 0.0 | 0 a 20 | Amplitud de la aceleración angular externa A·cos(Ωt). |
| Frecuencia de excitación | rad/s | 2.0 | 0.01 a 20 | Frecuencia angular de la fuerza externa; un ciclo dura 2π/Ω. |

### Supuestos

- Masa puntual, varilla sin masa y pivote fijo.
- El modelo incluye gravedad uniforme, rozamiento viscoso y un par externo prescrito.

### Preguntas para investigar

- Compara 5° y 120°: ¿sigue siendo válido T ≈ 2π√(L/g)?
- Con excitación cero, ¿cómo cambia la energía al aumentar el rozamiento?

### Ecuaciones

Ecuación angular no lineal:

$$\ddot{\theta}+\eta\dot{\theta}+(g/L)\sin\theta=A\cos(\Omega t)$$

Posición en el plano vertical:

$$x=L\sin\theta,\quad z=-L\cos\theta$$

Energía referida al punto más bajo:

$$E=\frac{1}{2} mL^2\dot{\theta}^2+mgL(1-\cos\theta)$$

Período aproximado para ángulos pequeños:

$$T_0=2\pi\sqrt{L/g}$$

### Ejemplos

- [Péndulo de ángulo pequeño](../examples/pendulum_small.json): Período cercano a 2π√(L/g) y energía constante.
- [Péndulo de gran amplitud](../examples/pendulum_large.json): El período supera la aproximación de ángulo pequeño.

### Referencias

- [OpenStax · Mecánica](https://openstax.org/details/books/university-physics-volume-1)

## 5. Péndulo doble

**Área:** Caos y dinámica.

Dos péndulos acoplados con masas y longitudes independientes, energía y trayectorias de ambas masas.

**Escena:** Geometría física en el plano XZ. Las varillas enlazan el pivote, la masa 1 y la masa 2.

**Duración:** 15.0 s por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Masa 1 | kg | 1.0 | 0.05 a 20 | Masa inercial del primer cuerpo. |
| Masa 2 | kg | 1.0 | 0.05 a 20 | Masa inercial del segundo cuerpo. |
| Longitud 1 | m | 1.0 | 0.1 a 5 | Distancia del pivote fijo a la primera masa. |
| Longitud 2 | m | 1.0 | 0.1 a 5 | Distancia entre la primera y la segunda masa. |
| Gravedad | m/s² | 9.80665 | 0.1 a 30 | Magnitud constante de la aceleración gravitatoria; actúa hacia −Z. |
| Ángulo 1 inicial | ° | 110.0 | -179 a 179 | Ángulo de la primera varilla respecto a la vertical inferior. |
| Ángulo 2 inicial | ° | -20.0 | -179 a 179 | Ángulo de la segunda varilla respecto a la vertical inferior. |
| Velocidad angular 1 | rad/s | 0.0 | -15 a 15 | Velocidad angular inicial de la primera varilla. |
| Velocidad angular 2 | rad/s | 0.0 | -15 a 15 | Velocidad angular inicial de la segunda varilla. |

### Supuestos

- Varillas rígidas y sin masa; masas puntuales.
- Sin fricción ni colisiones entre las masas o las varillas.

### Preguntas para investigar

- Compara proyectos que difieran 0.01° en θ₁.
- Reduce tolerancias y observa el balance de energía.

### Ecuaciones

Acoplamiento en la matriz de masas:

$$\Delta=\theta_1-\theta_2,\quad M_{12}=m_2L_1L_2\cos\Delta$$

Elementos diagonales; se resuelve M·θ″ = f:

$$M_{11}=(m_1+m_2)L_1^2,\quad M_{22}=m_2L_2^2$$

Energía cinética acoplada:

$$K=\frac{1}{2}M_{11}\dot{\theta}_1^2+\frac{1}{2}M_{22}\dot{\theta}_2^2+M_{12}\dot{\theta}_1\dot{\theta}_2$$

Energía potencial; E = K + U:

$$U=-(m_1+m_2)gL_1\cos\theta_1-m_2gL_2\cos\theta_2$$

### Ejemplos

- [Péndulo doble energético](../examples/double_chaos.json): Movimiento complejo; conserva la energía aunque la trayectoria sea sensible.
- [Péndulo doble de baja amplitud](../examples/double_small.json): Observa modos acoplados cerca del equilibrio.

### Referencias

- [OpenStax · Mecánica](https://openstax.org/details/books/university-physics-volume-1)

## 6. Proyectil 3D con viento

**Área:** Mecánica.

Lanzamiento tridimensional con gravedad, arrastre cuadrático, viento vectorial y evento de llegada al suelo.

**Escena:** Trayectoria espacial real en metros. La simulación finaliza al cruzar el plano del suelo z = 0 o al alcanzar T.

**Duración:** 15.0 s por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Masa | kg | 0.145 | 0.001 a 100 | Masa inercial positiva; escala la energía y la respuesta a la fuerza. |
| Rapidez inicial | m/s | 35.0 | 0.01 a 500 | Magnitud de la velocidad inicial; elevación y azimut fijan sus componentes. |
| Elevación | ° | 40.0 | -80 a 90 | Ángulo de lanzamiento respecto al plano horizontal. |
| Azimut | ° | 20.0 | -180 a 180 | Ángulo en XY, medido desde +X hacia +Y. |
| Altura inicial | m | 2.0 | 0.001 a 1000 | Altura inicial positiva sobre el suelo z = 0. |
| Gravedad | m/s² | 9.80665 | 0.01 a 30 | Magnitud constante de la aceleración gravitatoria; actúa hacia −Z. |
| Densidad del aire | kg/m³ | 1.225 | 0 a 10 | Densidad constante del aire; cero recupera el modelo sin arrastre. |
| Coeficiente Cd | adimensional | 0.47 | 0 a 3 | Coeficiente adimensional de arrastre cuadrático, supuesto constante. |
| Área frontal | m² | 0.0042 | 0 a 2 | Área frontal usada en la fuerza ρ·Cd·A·\|v−w\|·(v−w)/2. |
| Viento X | m/s | 5.0 | -100 a 100 | Componente X de la velocidad constante del aire. |
| Viento Y | m/s | 0.0 | -100 a 100 | Componente Y de la velocidad constante del aire. |
| Viento Z | m/s | 0.0 | -30 a 30 | Componente vertical de la velocidad constante del aire. |

### Supuestos

- Gravedad y viento uniformes; densidad y Cd constantes.
- No incluye sustentación, rotación, rebotes ni variación atmosférica.

### Preguntas para investigar

- Pon densidad = 0 y compara con el tiro parabólico analítico.
- Invierte el viento lateral y compara el punto de impacto.

### Ecuaciones

Velocidad relativa al viento:

$$\dot{\mathbf{r}}=\mathbf{v},\quad \mathbf{u}=\mathbf{v}-\mathbf{w}$$

Gravedad y arrastre cuadrático:

$$m\dot{\mathbf{v}}=m\mathbf{g}-\frac{1}{2}\rho C_D A|\mathbf{u}|\mathbf{u}$$

Referencia de vacío:

$$z(t)=z_0+v_{z0}t-\frac{1}{2}gt^2\quad(\rho=0)$$

Energía mecánica; el viento puede transferir energía:

$$E=\frac{1}{2}m|\mathbf{v}|^2+mgz$$

### Ejemplos

- [Tiro parabólico en vacío](../examples/projectile_vacuum.json): La trayectoria coincide con la parábola analítica hasta tocar el suelo.
- [Proyectil con viento cruzado](../examples/projectile_wind.json): El arrastre y el viento lateral cambian el alcance y la desviación.

### Referencias

- [OpenStax · Mecánica](https://openstax.org/details/books/university-physics-volume-1)

## 7. Órbita gravitatoria

**Área:** Mecánica.

Órbita de prueba alrededor de una masa central, con excentricidad e inclinación y diagnósticos de invariantes.

**Escena:** Posición espacial en kilómetros. El punto de origen es la masa central; el eje temporal no forma parte de la geometría.

**Duración:** 2.0 períodos por defecto; rango 0.1 a 20.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Masa central | kg | 5.9722e+24 | 1e+10 a 1e+32 | Masa central fija que define μ = G·M; la masa orbitante es de prueba. |
| Semieje mayor | km | 10000.0 | 1 a 1e+09 | Semieje mayor a; se convierte de kilómetros a metros. |
| Excentricidad | adimensional | 0.3 | 0 a 0.95 | Excentricidad de una órbita elíptica; cero es circular. |
| Inclinación | ° | 35.0 | 0 a 180 | Rotación del plano orbital o de dispersión alrededor de X. |

### Supuestos

- Partícula de prueba y campo newtoniano central; masa central fija.
- Sin tamaño de los cuerpos, colisiones, relatividad, atmósfera ni perturbaciones.

### Preguntas para investigar

- Para e = 0, verifica r constante y el período de Kepler.
- Compara conservación de energía y momento angular al refinar el paso.

### Ecuaciones

Aceleración gravitatoria central:

$$\ddot{\mathbf{r}}=-GM\mathbf{r}/r^3$$

Período kepleriano:

$$T=2\pi\sqrt{a^3/(GM)}$$

Energía específica:

$$\epsilon=|\mathbf{v}|^2/2-GM/r=-GM/(2a)$$

Momento angular específico conservado:

$$\mathbf{h}=\mathbf{r}\times\mathbf{v}$$

### Ejemplos

- [Órbita circular](../examples/orbit_circle.json): El radio es constante y una vuelta tarda un período.
- [Órbita elíptica inclinada](../examples/orbit_ellipse.json): Mayor rapidez cerca del periastro; energía y momento angular conservados.

### Referencias

- [OpenStax · Mecánica](https://openstax.org/details/books/university-physics-volume-1)
- [NIST · constantes CODATA](https://physics.nist.gov/cuu/Constants/)

## 8. Osciladores acoplados

**Área:** Mecánica.

Dos grados de libertad, resortes y amortiguamiento para observar batidos y transferencia de energía.

**Escena:** Espacio de estados (x₁, x₂, t): el tercer eje representa tiempo; no es una trayectoria espacial.

**Duración:** 40.0 s por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Masa 1 | kg | 1.0 | 0.05 a 20 | Masa inercial del primer cuerpo. |
| Masa 2 | kg | 1.0 | 0.05 a 20 | Masa inercial del segundo cuerpo. |
| Rigidez 1 | N/m | 4.0 | 0.01 a 100 | Rigidez del resorte que une la primera masa a su equilibrio. |
| Rigidez 2 | N/m | 4.0 | 0.01 a 100 | Rigidez del resorte que une la segunda masa a su equilibrio. |
| Acoplamiento | N/m | 0.8 | 0 a 100 | Rigidez del resorte que acopla ambas masas. |
| Amortiguamiento común | kg/s | 0.0 | 0 a 10 | Coeficiente disipativo; sus unidades dependen de la ecuación del modelo seleccionado. |
| Posición inicial 1 | m | 1.0 | -10 a 10 | Desplazamiento inicial de la primera masa desde el equilibrio. |
| Posición inicial 2 | m | 0.0 | -10 a 10 | Desplazamiento inicial de la segunda masa desde el equilibrio. |
| Velocidad inicial 1 | m/s | 0.0 | -20 a 20 | Velocidad inicial de la primera masa. |
| Velocidad inicial 2 | m/s | 0.0 | -20 a 20 | Velocidad inicial de la segunda masa. |

### Supuestos

- Resortes lineales; desplazamientos medidos desde el equilibrio.
- Amortiguamiento viscoso igual en ambas masas.

### Preguntas para investigar

- Con masas y resortes iguales, compara modos en fase y en oposición.
- Excita solo la masa 1 y observa la transferencia de energía.

### Ecuaciones

Primera masa:

$$m_1\ddot{x}_1=-k_1x_1-k_c(x_1-x_2)-c\dot{x}_1$$

Segunda masa:

$$m_2\ddot{x}_2=-k_2x_2-k_c(x_2-x_1)-c\dot{x}_2$$

Energía potencial total:

$$U=\frac{1}{2}k_1x_1^2+\frac{1}{2}k_2x_2^2+\frac{1}{2}k_c(x_1-x_2)^2$$

Modos normales para m₁=m₂ y k₁=k₂:

$$\omega_s=\sqrt{k/m},\quad\omega_a=\sqrt{(k+2k_c)/m}$$

### Ejemplos

- [Batidos y transferencia](../examples/coupled_beats.json): La excitación pasa de una masa a la otra.
- [Modo simétrico](../examples/coupled_mode.json): Ambas masas se mueven juntas y el resorte de acoplamiento no se deforma.

### Referencias

- [OpenStax · Mecánica](https://openstax.org/details/books/university-physics-volume-1)

## 9. Oscilador de Duffing

**Área:** Caos y dinámica.

Oscilador forzado no lineal con espacio de fases, sección estroboscópica y espectro de frecuencia.

**Escena:** Espacio de estados (x, v, t), con tiempo adimensional como tercer eje.

**Duración:** 100.0 adimensional por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Coeficiente α | adimensional | -1.0 | -5 a 10 | Coeficiente de rigidez lineal de Duffing; negativo permite dos pozos de potencial. |
| Coeficiente β | adimensional | 1.0 | 0.01 a 10 | Rigidez cúbica positiva de Duffing, que limita el potencial a amplitudes grandes. |
| Amortiguamiento δ | adimensional | 0.2 | 0 a 5 | Coeficiente disipativo; sus unidades dependen de la ecuación del modelo seleccionado. |
| Forzamiento γ | adimensional | 0.3 | 0 a 5 | Amplitud del forzamiento armónico de Duffing. |
| Frecuencia Ω | adimensional | 1.2 | 0.05 a 10 | Frecuencia angular de la fuerza externa; un ciclo dura 2π/Ω. |
| Posición inicial | adimensional | 0.1 | -10 a 10 | Posición inicial adimensional. |
| Velocidad inicial | adimensional | 0.0 | -10 a 10 | Velocidad inicial adimensional. |

### Supuestos

- Modelo adimensional, forzamiento armónico y rigidez cúbica positiva.
- FFT de la segunda mitad con ventana Hann; la resolución depende de la duración.

### Preguntas para investigar

- Compara forzamientos 0.1 y 0.3.
- Observa puntos cada período de la fuerza; pocos puntos no bastan para caracterizar el caos.

### Ecuaciones

Ecuación de Duffing:

$$\ddot{x}+\delta\dot{x}+\alpha x+\beta x^3=\gamma\cos(\Omega t)$$

Energía del sistema sin forzamiento ni disipación:

$$H=\frac{1}{2}v^2+\frac{1}{2}\alpha x^2+\frac{1}{4}\beta x^4$$

Sección estroboscópica:

$$t_n=2\pi n/\Omega$$

Espectro FFT con ventana:

$$X_k=\sum_n w_n(x_n-\bar x)e^{-2\pi i kn/N}$$

### Ejemplos

- [Duffing: forzamiento débil](../examples/duffing_periodic.json): Compara la sección estroboscópica y el espectro con el caso de forzamiento mayor.
- [Duffing: forzamiento no lineal](../examples/duffing_nonlinear.json): La respuesta puede cambiar mucho con las condiciones iniciales y el transitorio.

### Referencias

- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)

## 10. Mapa logístico y bifurcaciones

**Área:** Caos y dinámica.

Iteración discreta, cobweb, exponente de Lyapunov de la órbita y barrido de bifurcaciones.

**Escena:** Coordenadas (n, xₙ, xₙ₊₁). La escena representa estados discretos, no posiciones espaciales.

**Variable de salida:** iteración. No se impone una duración temporal.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Parámetro r | adimensional | 3.8 | 0 a 4 | Parámetro de crecimiento del mapa logístico; 0 ≤ r ≤ 4 mantiene el intervalo [0,1]. |
| Estado inicial | adimensional | 0.2 | 1e-08 a 1 | Estado inicial del mapa dentro del intervalo abierto (0,1). |
| Iteraciones | adimensional | 1200 | 300 a 5000 | Longitud de la órbita del mapa elegida para análisis. |
| Descartar primeras | adimensional | 300 | 0 a 4000 | Iteraciones iniciales que se excluyen de la estimación de Lyapunov y del histograma. |
| r mínimo del barrido | adimensional | 2.5 | 0 a 4 | Extremo inferior del barrido de bifurcaciones. |
| r máximo del barrido | adimensional | 4.0 | 0 a 4 | Extremo superior del barrido de bifurcaciones. |
| Valores r del barrido | adimensional | 250 | 50 a 500 | Número de valores uniformemente espaciados del parámetro r. |

### Supuestos

- Mapa matemático adimensional; aritmética float64.
- El exponente se estima sobre una órbita finita después del transitorio.

### Preguntas para investigar

- Compara r = 2.8, 3.2 y 4.
- Aumenta el transitorio y la longitud de la órbita antes de concluir estabilidad.

### Ecuaciones

Regla de evolución discreta:

$$x_{n+1}=rx_n(1-x_n)$$

Derivada local del mapa:

$$f^{\prime}(x)=r(1-2x)$$

Estimación del exponente de Lyapunov:

$$\lambda_N=\frac{1}{N}\sum_n\log|r(1-2x_n)|$$

Puntos fijos; el segundo requiere r > 0:

$$x^*=0,\quad x^*=1-1/r$$

### Ejemplos

- [Mapa: punto fijo](../examples/logistic_fixed.json): Con r = 2.8, la órbita converge a 1 − 1/r.
- [Mapa: r = 4](../examples/logistic_chaos.json): Para una órbita típica, el exponente finito se acerca a ln 2.

### Referencias


## 11. Partícula relativista en campos E/B

**Área:** Partículas y cuántica.

Trayectoria de una partícula cargada en campos uniformes, con momento relativista, energía y rapidez.

**Escena:** Trayectoria espacial en milímetros. Se integra el momento relativista con variables normalizadas; el tiempo de salida se muestra en ns.

**Duración:** 5.0 ns por defecto; rango 0.001 a 10000.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Partícula | adimensional | Electrón e⁻ | Electrón e⁻, Positrón e⁺, Muón μ⁻, Antimuón μ⁺, Protón p, Antiprotón p̄, Partícula α | Especie que fija la masa en reposo y la carga del proyectil; consulta el catálogo de partículas. |
| Energía cinética inicial | MeV | 0.01 | 1e-06 a 100000 | Energía cinética inicial, excluyendo la energía de reposo mc². |
| Ángulo polar respecto a +Z | ° | 65.0 | 0 a 180 | Ángulo de la velocidad inicial respecto a +Z; no necesariamente respecto al vector B. |
| Azimut inicial | ° | 0.0 | -180 a 180 | Ángulo en XY, medido desde +X hacia +Y. |
| Campo Eₓ | kV/m | 0.0 | -1000 a 1000 | Componente X del campo eléctrico uniforme; entrada en kV/m. |
| Campo Eᵧ | kV/m | 0.0 | -1000 a 1000 | Componente Y del campo eléctrico uniforme; entrada en kV/m. |
| Campo E_z | kV/m | 0.0 | -1000 a 1000 | Componente Z del campo eléctrico uniforme; entrada en kV/m. |
| Campo Bₓ | T | 0.0 | -10 a 10 | Componente X del campo magnético uniforme en teslas. |
| Campo Bᵧ | T | 0.0 | -10 a 10 | Componente Y del campo magnético uniforme en teslas. |
| Campo B_z | T | 0.02 | -10 a 10 | Componente Z del campo magnético uniforme en teslas. |
| Posición X inicial | mm | 0.0 | -1000 a 1000 | Posición espacial inicial X; entrada en milímetros. |
| Posición Y inicial | mm | 0.0 | -1000 a 1000 | Posición espacial inicial Y; entrada en milímetros. |
| Posición Z inicial | mm | 0.0 | -1000 a 1000 | Posición espacial inicial Z; entrada en milímetros. |

### Supuestos

- Partícula puntual y campos externos uniformes, sin colisiones, espín ni emisión de radiación.
- La trayectoria de muones se calcula sin eliminar partículas por decaimiento; usa el módulo de decaimiento para poblaciones.

### Preguntas para investigar

- Invierte la carga eligiendo electrón y positrón: ¿cambia el sentido de giro?
- Con E = 0, verifica energía constante. Con B = 0 y E paralelo, verifica dp/dt = qE.

### Ecuaciones

Velocidad y factor relativista:

$$\dot{\mathbf{r}}=\mathbf{p}/(\gamma m),\quad \gamma=\sqrt{1+|\mathbf{p}/(mc)|^2}$$

Fuerza de Lorentz:

$$\dot{\mathbf{p}}=q(\mathbf{E}+\mathbf{v}\times\mathbf{B})$$

Relación energía–momento:

$$E^2=p^2c^2+m^2c^4,\quad K=(\gamma-1)mc^2$$

Trabajo eléctrico y radio de Larmor en campo magnético uniforme:

$$\dot{E}=q\mathbf{E}\cdot\mathbf{v},\quad r_L=p_\perp/(|q|B)$$

### Ejemplos

- [Electrón: hélice magnética](../examples/electron_helix.json): La rapidez y la energía se conservan; el campo magnético curva la trayectoria.
- [Positrón: giro opuesto](../examples/positron_helix.json): Con las mismas condiciones, el signo de la carga invierte el sentido de giro.
- [Protón: aceleración eléctrica](../examples/electric_acceleration.json): Con B = 0, p_z crece linealmente y la rapidez permanece menor que c.

### Referencias

- [OpenStax · Electromagnetismo](https://openstax.org/details/books/university-physics-volume-2)
- [OpenStax · Relatividad y cuántica](https://openstax.org/details/books/university-physics-volume-3)
- [NIST · constantes CODATA](https://physics.nist.gov/cuu/Constants/)
- [Particle Data Group · tablas y revisiones](https://pdg.lbl.gov/)

## 12. Dispersión de Rutherford

**Área:** Partículas y cuántica.

Dispersión coulombiana repulsiva con trayectoria hiperbólica, ángulo asintótico y sección eficaz diferencial.

**Escena:** Trayectoria clásica en femtómetros alrededor de un blanco puntual fijo. El ángulo y la sección eficaz se refieren al régimen asintótico.

**Variable de salida:** s. No se impone una duración temporal.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Proyectil | adimensional | Partícula α | Partícula α, Protón | Especie que fija la masa en reposo y la carga del proyectil; consulta el catálogo de partículas. |
| Energía cinética incidente | MeV | 5.0 | 0.001 a 100 | Energía cinética o energía incidente en las unidades indicadas; compara con las escalas del modelo. |
| Z del blanco | adimensional | 79 | 1 a 92 | Número de protones del blanco; su carga es Z·e. |
| A del blanco (radio estimado) | adimensional | 197 | 1 a 238 | Número másico usado solo para estimar 1.2·A^(1/3) fm; no introduce retroceso nuclear. |
| Parámetro de impacto b | fm | 50.0 | 0.1 a 10000 | Distancia perpendicular asintótica entre la trayectoria incidente y el centro del blanco. |
| Extensión hiperbólica | adimensional | 3.0 | 1 a 5 | Extremo del parámetro hiperbólico; amplía la ventana finita dibujada sin cambiar el ángulo asintótico. |
| Rotación del plano | ° | 25.0 | -180 a 180 | Rotación del plano orbital o de dispersión alrededor de X. |

### Supuestos

- Blanco infinitamente pesado y puntual; interacción coulombiana repulsiva no relativista.
- Sin apantallamiento, fuerza nuclear, recoil, estructura del núcleo ni pérdida de energía.
- A solo estima el radio nuclear 1.2·A^(1/3) fm; no modifica el potencial.

### Preguntas para investigar

- Duplica la energía o el impacto y compara el ángulo.
- Compara la distancia mínima con el radio nuclear estimado antes de interpretar el resultado.

### Ecuaciones

Escala coulombiana de la órbita:

$$\kappa=Z_1Z_2e^2/(4\pi\epsilon_0),\quad a=\kappa/(2K)$$

Ángulo de dispersión asintótico:

$$\theta=2\arctan(a/b)$$

Distancia mínima de acercamiento:

$$r_{\min}=a+\sqrt{a^2+b^2}$$

Sección eficaz diferencial, calculada en fm²/sr:

$$\frac{d\sigma}{d\Omega}=\left(\frac{\kappa}{4K}\right)^2\sin^{-4}(\theta/2)$$

### Ejemplos

- [Alfa sobre oro](../examples/rutherford_gold.json): Para 5 MeV y b = 50 fm, la dispersión asintótica es de unas decenas de grados.
- [Rutherford: impacto lejano](../examples/rutherford_far.json): Al aumentar b, disminuye el ángulo de desviación.

### Referencias

- [OpenStax · Relatividad y cuántica](https://openstax.org/details/books/university-physics-volume-3)
- [NIST · constantes CODATA](https://physics.nist.gov/cuu/Constants/)

## 13. Decaimiento radiactivo y detección

**Área:** Partículas y cuántica.

Población estocástica de núcleos o partículas inestables, ley exponencial, eficiencia del detector y fondo.

**Escena:** Espacio de observables (tiempo, supervivientes, actividad esperada). No representa posiciones de partículas individuales.

**Duración:** 50.0 s por defecto; rango 1e-12 a 1e+10.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Población inicial N₀ | adimensional | 10000 | 100 a 1e+06 | Número de objetos inestables independientes al inicio. |
| Semivida t½ | s | 10.0 | 1e-12 a 1e+10 | Tiempo en el que la población esperada cae a la mitad; la vida media es t½/ln 2. |
| Eficiencia de detección | adimensional | 0.7 | 0 a 1 | Probabilidad de registrar cada decaimiento; no incluye tiempo muerto. |
| Fondo de detección | cuentas/s | 2.0 | 0 a 1e+09 | Tasa media de cuentas espurias de un proceso Poisson independiente. |

### Supuestos

- Decaimientos independientes con tasa constante, un solo canal efectivo y sin cadena de descendientes.
- Detección binomial independiente; fondo Poisson. No incluye tiempo muerto ni resolución energética.
- Bandas de supervivientes: cuantiles binomiales para cada tiempo, no banda simultánea.

### Preguntas para investigar

- Compara t½ con la vida media τ = t½/ln 2.
- Pon eficiencia = 1 y fondo = 0; luego observa el efecto del detector.

### Ecuaciones

Constante de decaimiento y vida media:

$$\lambda=\ln 2/t_{1/2},\quad \tau=1/\lambda$$

Supervivientes y actividad esperada:

$$\mathbb{E}[N(t)]=N_0e^{-\lambda t},\quad A(t)=\lambda N_0e^{-\lambda t}$$

Distribución puntual de supervivientes:

$$N(t)\sim\operatorname{Binomial}(N_0,e^{-\lambda t})$$

Cuentas detectadas por intervalo:

$$C_i\sim\operatorname{Binomial}(D_i,\epsilon)+\operatorname{Poisson}(b\Delta t_i)$$

### Ejemplos

- [Semivida de 10 s](../examples/decay_population.json): La población esperada queda en la mitad después de 10 s.
- [Población de muones en reposo](../examples/muon_lifetime.json): Vida media τ ≈ 2.1969811 μs; la semivida es τ·ln 2.

### Referencias

- [OpenStax · Relatividad y cuántica](https://openstax.org/details/books/university-physics-volume-3)
- [Particle Data Group · tablas y revisiones](https://pdg.lbl.gov/)

## 14. Decaimiento relativista de dos cuerpos

**Área:** Partículas y cuántica.

Cinemática de un decaimiento M → 1 + 2: marcos de reposo y laboratorio, boost y conservación del cuatro-momento.

**Escena:** Esquema de vuelo libre en centímetros después de un vértice en el origen. Se muestran ambas hijas; no incluye un detector ni una distribución de canales.

**Duración:** 1.0 ns por defecto; rango 0.001 a 100.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Masa de la madre M | MeV/c² | 139.57039 | 0.001 a 1e+06 | Masa de la madre en reposo. Debe ser al menos la suma de las masas hijas. |
| Masa hija 1 | MeV/c² | 105.6583755 | 0 a 1e+06 | Masa en reposo de la primera hija; cero es la aproximación sin masa. |
| Masa hija 2 | MeV/c² | 0.0 | 0 a 1e+06 | Masa en reposo de la segunda hija; cero es la aproximación sin masa. |
| Energía cinética de la madre | MeV | 300.0 | 0 a 1e+07 | Energía cinética de la madre en laboratorio; el boost apunta hacia +Z. |
| Ángulo polar en reposo | ° | 65.0 | 0 a 180 | Ángulo de la hija 1 en el marco de reposo respecto a la dirección del boost +Z. |
| Azimut en reposo | ° | 20.0 | -180 a 180 | Azimut de la hija 1 en el marco de reposo; la hija 2 lleva momento opuesto. |

### Supuestos

- Un único evento de dos cuerpos; c = 1 en los cuatro-momentos (MeV y MeV/c).
- Masas fijas, sin anchura, polarización, elementos de matriz ni interacciones posteriores.
- Los ejemplos con neutrino usan masa nula como aproximación cinemática.

### Preguntas para investigar

- Carga π⁺ → μ⁺ν y compara madre en reposo y madre en movimiento.
- Verifica que la suma de los cuatro-momentos de las hijas coincide con el de la madre.

### Ecuaciones

Momento en el marco de reposo, c = 1:

$$p^*=\frac{\sqrt{[M^2-(m_1+m_2)^2][M^2-(m_1-m_2)^2]}}{2M}$$

Energías en reposo de la madre:

$$E_i^*=\sqrt{(p^*)^2+m_i^2}$$

Boost a lo largo de +Z:

$$E'=\gamma(E+\beta p_z),\quad p_z'=\gamma(p_z+\beta E)$$

Conservación y masas invariantes:

$$P_M^\mu=P_1^\mu+P_2^\mu,\quad E_i^2-|\mathbf{p}_i|^2=m_i^2$$

### Ejemplos

- [π⁺ → μ⁺ + ν: madre en reposo](../examples/pion_rest.json): Las hijas tienen momentos opuestos de igual magnitud; neutrino tratado como sin masa.
- [π⁺ → μ⁺ + ν: laboratorio](../examples/pion_boost.json): El boost cambia energías y ángulos, conservando el cuatro-momento.
- [K⁺ → π⁺ + π⁰](../examples/kaon_two_pions.json): Ambas masas hijas son distintas; compara las energías en reposo y laboratorio.
- [Z⁰ → e⁺ + e⁻](../examples/z_electrons.json): En reposo, las energías de las hijas son aproximadamente M_Z/2.

### Referencias

- [Particle Data Group · tablas y revisiones](https://pdg.lbl.gov/)
- [OpenStax · Relatividad y cuántica](https://openstax.org/details/books/university-physics-volume-3)

## 15. Barrera cuántica 1D

**Área:** Partículas y cuántica.

Estado estacionario sobre una barrera rectangular: función de onda compleja, densidad y coeficientes de transmisión y reflexión.

**Escena:** Representación (x, Re ψ, Im ψ) de una función de onda estacionaria. El eje x es espacial; las amplitudes complejas no son coordenadas de una trayectoria.

**Variable de salida:** posición (nm). No se impone una duración temporal.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Energía incidente | eV | 2.0 | 0.001 a 100 | Energía cinética o energía incidente en las unidades indicadas; compara con las escalas del modelo. |
| Altura de barrera | eV | 5.0 | 0 a 100 | Altura constante del potencial rectangular entre x=0 y x=a; fuera, V=0. |
| Anchura de barrera | nm | 0.4 | 0.01 a 5 | Anchura a de la barrera rectangular; entrada en nanómetros. |
| Masa efectiva / mₑ | adimensional | 1.0 | 0.01 a 10 | Masa constante en la ecuación de Schrödinger, expresada como múltiplo de la masa del electrón. |
| Energía máxima del barrido | eV | 12.0 | 0.01 a 200 | Extremo superior del barrido analítico de transmisión frente a energía. |

### Supuestos

- Ecuación de Schrödinger no relativista 1D; barrera rectangular y masa efectiva constante.
- Estado estacionario de flujo incidente unitario en amplitud: |ψ|² no está normalizada a una partícula.
- No modela colapso, evolución temporal de un paquete ni teoría cuántica de campos.

### Preguntas para investigar

- Compara E < V₀, E = V₀ y E > V₀.
- Busca resonancias de transmisión y verifica R + T = 1.

### Ecuaciones

Ecuación estacionaria de Schrödinger:

$$-\frac{\hbar^2}{2m}\psi^{\prime\prime}+V(x)\psi=E\psi$$

Número de onda; q es imaginario bajo la barrera:

$$k=\sqrt{2mE}/\hbar,\quad q=\sqrt{2m(E-V_0)}/\hbar$$

Flujo conservado para potenciales iguales a ambos lados:

$$T=|t|^2,\quad R=|r|^2,\quad R+T=1$$

Límite regular en la cima de la barrera:

$$T(E=V_0)=[1+mV_0a^2/(2\hbar^2)]^{-1}$$

### Ejemplos

- [Túnel: energía bajo la barrera](../examples/quantum_tunnel.json): La transmisión es positiva aunque E < V₀, y R + T ≈ 1.
- [Energía sobre la barrera](../examples/quantum_above.json): La reflexión puede persistir por interferencia aunque E > V₀.
- [Energía igual a la barrera](../examples/quantum_top.json): La solución usa el límite regular, sin dividir por q = 0.

### Referencias

- [OpenStax · Relatividad y cuántica](https://openstax.org/details/books/university-physics-volume-3)
- [NIST · constantes CODATA](https://physics.nist.gov/cuu/Constants/)

## 16. Gas de esferas elásticas

**Área:** Simuladores de partículas.

Muchas esferas en un recipiente 3D: choques, rapidez, energía y presión calculada en las paredes.

**Escena:** Posiciones físicas en metros. Paredes fijas; hasta cinco colas de trayectoria. Los puntos indican centros y su tamaño dibujado es ilustrativo.

**Duración:** 8.0 s por defecto; rango 0.1 a 40.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Número de esferas | adimensional | 36 | 2 a 96 | Masas y radios iguales; coste por pares O(N²). |
| Lado del recipiente L | m | 2.0 | 0.5 a 10 | Recipiente cúbico centrado en el origen. |
| Radio físico r | m | 0.06 | 0.005 a 0.3 | Interviene en los choques, aunque el marcador 3D es ilustrativo. |
| Masa de cada esfera | kg | 0.01 | 0.0001 a 10 | Masa común para impulsos y energía. |
| Rapidez RMS inicial | m/s | 1.0 | 0.05 a 5 | Velocidades normales con momento inicial nulo y RMS reescalada. |
| Paso máximo Δt | s | 0.005 | 0.0001 a 0.05 | Se limita además para que el desplazamiento no supere 0.3r. |

### Supuestos

- Modelo clásico no relativista de esferas iguales, duras y lisas; sin gravedad.
- Choques y paredes elásticos; contacto aproximado por subpasos y corrección de penetración.
- Inicialización diluida sin solapamientos: volumen ocupado ≤ 8 %, radio < L/6.
- Presión acumulada por impulso; referencia ideal diluida 2K/(3V).

### Preguntas para investigar

- Duplica la rapidez RMS: ¿cómo cambia la energía y la presión?
- Reduce Δt a la mitad y compara presión media y conteo de choques.

### Ecuaciones

Energía cinética de las esferas:

$$K=\frac{m}{2}\sum_i |\mathbf{v}_i|^2$$

Impulso elástico entre masas iguales; j recibe el opuesto:

$$\mathbf{v}_i^\prime=\mathbf{v}_i-[(\mathbf{v}_i-\mathbf{v}_j)\cdot\mathbf{n}]\mathbf{n}$$

Presión media acumulada sobre las seis paredes:

$$P(t)=\frac{\sum |\Delta p_{\rm pared}|}{6L^2t}$$

Referencia cinética de gas diluido:

$$P_{\rm diluido}=2K/(3L^3)$$

### Ejemplos

- [Gas diluido: choques y presión](../examples/gas_dilute.json): La energía se conserva; la presión acumulada fluctúa y se aproxima a la referencia diluida.
- [Gas: duplicar rapidez](../examples/gas_fast.json): Al duplicar RMS se cuadruplica K; compara presiones con igual duración.
- [Dos esferas y el recipiente](../examples/gas_pair.json): Sigue cada centro y observa intercambios de momento entre esferas y paredes.

### Referencias

- [OpenStax · Mecánica](https://openstax.org/details/books/university-physics-volume-1)

## 17. N cuerpos: gravedad y cargas

**Área:** Simuladores de partículas.

Partículas con fuerzas mutuas, potencial suavizado, momento, energía y comparación de pasos.

**Escena:** Posiciones en unidades reducidas; no hay paredes. En modo eléctrico el color distingue signos. Colas para hasta ocho partículas.

**Duración:** 6.0 uT por defecto; rango 0.1 a 30.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Número de partículas | adimensional | 40 | 2 a 128 | Interacciones directas por pares O(N²). |
| Interacción | adimensional | Gravedad atractiva | Gravedad atractiva, Cargas de signos alternos | Gravedad: Uij=−g·m²/√(r²+ε²). Eléctrica: Uij=k·qi·qj/√(r²+ε²). |
| Geometría inicial | adimensional | Disco delgado | Disco delgado, Nube 3D | Distribución aleatoria reproducible, centrada en el origen. |
| Masa por partícula | uM | 0.02 | 0.001 a 1 | Masas iguales; unidades reducidas, sin conversión SI automática. |
| Magnitud de carga \|q\| | uQ | 0.08 | 0 a 0.5 | Solo interviene en el modo eléctrico; alterna signos. |
| Acoplamiento g o k | reducido | 1.0 | 0.01 a 5 | Constante de fuerza en las unidades reducidas elegidas. |
| Suavizado ε | uL | 0.12 | 0.03 a 0.5 | Parte del potencial; evita singularidades. No es una tolerancia numérica. |
| Escala de radio inicial | uL | 1.0 | 0.3 a 5 | Radio máximo antes de centrar y aplanar el disco. |
| Rapidez tangencial inicial | uL/uT | 0.35 | 0 a 2 | Rotación alrededor del eje Z. |
| Dispersión RMS de rapidez | uL/uT | 0.1 | 0 a 2 | Componente aleatoria normal; se elimina la velocidad del centro de masa. |
| Paso máximo Δt | uT | 0.005 | 0.0001 a 0.03 | Velocity Verlet, repetido con Δt/2 para diagnosticar convergencia. |

### Supuestos

- Partículas clásicas iguales con potencial de Plummer suavizado; fronteras abiertas.
- uE = uM·uL²/uT²; las magnitudes no se convierten automáticamente a SI.
- Sin impactos, fusiones, radiación ni relatividad; las partículas pueden atravesarse.
- La gravedad y las cargas eléctricas son modelos clásicos; no incluyen teoría cuántica de campos.

### Preguntas para investigar

- Compara nube y disco conservando la semilla.
- ¿Cómo cambian energía y estructura al reducir ε y Δt?
- En modo eléctrico, compara nube con carga cero y con signos alternos.

### Ecuaciones

Cij = −g mi mj en gravedad; k qi qj en electrostática:

$$U_{ij}=C_{ij}/\sqrt{r_{ij}^2+\epsilon^2}$$

Fuerza central, con rij = ri − rj:

$$\mathbf{F}_{ij}=C_{ij}\mathbf{r}_{ij}/(r_{ij}^2+\epsilon^2)^{3/2}$$

Primer paso de Velocity Verlet:

$$\mathbf{r}_{n+1}=\mathbf{r}_n+h\mathbf{v}_n+\frac{h^2}{2}\mathbf{a}_n$$

Segundo paso; se comparan h y h/2:

$$\mathbf{v}_{n+1}=\mathbf{v}_n+\frac{h}{2}(\mathbf{a}_n+\mathbf{a}_{n+1})$$

### Ejemplos

- [Disco de partículas gravitantes](../examples/gravity_disk.json): Investiga la estructura colectiva y verifica energía, momento y comparación Δt/2.
- [Colapso de nube suavizada](../examples/gravity_cloud.json): Con poca velocidad inicial la gravedad contrae la nube; ε evita singularidades.
- [Nube de cargas alternas](../examples/electric_cloud.json): Cargas opuestas se atraen y las iguales se repelen; la fuerza está suavizada.

### Referencias

- [OpenStax · Mecánica](https://openstax.org/details/books/university-physics-volume-1)
- [OpenStax · Electromagnetismo](https://openstax.org/details/books/university-physics-volume-2)

## 18. Atractor de Rössler

**Área:** Caos y dinámica.

Atractor 3D, trayectoria vecina y barrido del parámetro c.

**Escena:** Espacio de estados adimensional (x, y, z). Ámbar: condición inicial vecina.

**Duración:** 60.0 adimensional por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Parámetro a | adimensional | 0.2 | 0.05 a 0.4 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Parámetro b | adimensional | 0.2 | 0.05 a 0.5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Parámetro c | adimensional | 5.7 | 1 a 10 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Estado inicial x | adimensional | 0.1 | -5 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Estado inicial y | adimensional | 0.1 | -5 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Estado inicial z | adimensional | 0.1 | 0 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Perturbación inicial δ | adimensional | 1e-05 | 1e-08 a 0.01 | Desplazamiento de la primera variable; en SIR transfiere δ de S a I conservando la población. |
| Inicio del tramo final / T | adimensional | 0.5 | 0 a 0.9 | Fracción de tiempo descartada en fase y barrido. SIR usa todo el intervalo para buscar el pico de I. |
| Barrido: c mínimo | adimensional | 2.0 | 1 a 10 | Inicio del barrido independiente. |
| Barrido: c máximo | adimensional | 6.0 | 1 a 10 | Final del barrido independiente. |
| Valores en el barrido | adimensional | 12 | 4 a 50 | Cada valor empieza desde la misma condición inicial. |

### Supuestos

- Variables y tiempo adimensionales; modelo determinista reducido.
- La distancia entre trayectorias no es un exponente de Lyapunov.
- El barrido muestra extremos muestreados a tiempo finito; no prueba una bifurcación asintótica.

### Preguntas para investigar

- Compara c=2 y c=5.7.
- Aumenta la duración y observa cómo cambia el barrido.

### Ecuaciones

Evolución de x:

$$\dot{x}=-y-z$$

Evolución de y:

$$\dot{y}=x+ay$$

Evolución de z:

$$\dot{z}=b+z(x-c)$$

Distancia entre estados vecinos:

$$d(t)=\|\mathbf{u}_\delta(t)-\mathbf{u}(t)\|_2$$

### Ejemplos

- [Rössler: atractor clásico](../examples/rossler_classic.json): Observa la estructura espiral y la separación de estados vecinos.
- [Rössler: c bajo](../examples/rossler_low.json): Compara el régimen de c=2 con el atractor de c=5.7.

### Referencias

- [Rössler (1976)](https://doi.org/10.1016/0375-9601(76)90101-8)
- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)

## 19. Oscilador de Van der Pol

**Área:** Caos y dinámica.

Ciclo límite y oscilación de relajación con campo de direcciones y barrido de μ.

**Escena:** Espacio ampliado (x, v, t). El tercer eje representa tiempo, no una coordenada física.

**Duración:** 40.0 adimensional por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| No linealidad μ | adimensional | 1.0 | 0 a 10 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Posición inicial | adimensional | 0.2 | -5 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Velocidad inicial | adimensional | 0.0 | -5 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Perturbación inicial δ | adimensional | 1e-05 | 1e-08 a 0.01 | Desplazamiento de la primera variable; en SIR transfiere δ de S a I conservando la población. |
| Inicio del tramo final / T | adimensional | 0.5 | 0 a 0.9 | Fracción de tiempo descartada en fase y barrido. SIR usa todo el intervalo para buscar el pico de I. |
| Barrido: μ mínimo | adimensional | 0.0 | 0 a 10 | Inicio del barrido independiente. |
| Barrido: μ máximo | adimensional | 5.0 | 0 a 10 | Final del barrido independiente. |
| Valores en el barrido | adimensional | 12 | 4 a 50 | Cada valor empieza desde la misma condición inicial. |

### Supuestos

- Variables y tiempo adimensionales; modelo determinista reducido.
- La distancia entre trayectorias no es un exponente de Lyapunov.
- El barrido muestra extremos muestreados a tiempo finito; no prueba una bifurcación asintótica.

### Preguntas para investigar

- Compara μ=0, μ=1 y μ=8.
- ¿Convergen dos amplitudes iniciales al mismo ciclo límite?

### Ecuaciones

Definición de velocidad:

$$\dot{x}=v$$

Amortiguamiento no lineal:

$$\dot{v}=\mu(1-x^2)v-x$$

Ecuación de Van der Pol:

$$\ddot{x}-\mu(1-x^2)\dot{x}+x=0$$

E=(x²+v²)/2: energía inyectada o disipada:

$$\dot{E}=\mu(1-x^2)v^2$$

### Ejemplos

- [Van der Pol: ciclo límite](../examples/vdp_cycle.json): Las oscilaciones alcanzan una amplitud sostenida por el amortiguamiento no lineal.
- [Van der Pol: relajación](../examples/vdp_relaxation.json): Con μ=8 aparecen tramos lentos y transiciones rápidas.

### Referencias

- [Scholarpedia · sistemas dinámicos](http://www.scholarpedia.org/article/Dynamical_systems)
- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)

## 20. Lotka–Volterra: presa y depredador

**Área:** Caos y dinámica.

Poblaciones continuas acopladas, integral primera, campo de direcciones y barrido del crecimiento.

**Escena:** Espacio ampliado (presas, depredadores, t), con poblaciones adimensionales continuas.

**Duración:** 30.0 adimensional por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Crecimiento de presas α | adimensional | 1.1 | 0.05 a 3 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Depredación β | adimensional | 0.4 | 0.05 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Conversión δ | adimensional | 0.1 | 0.05 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Mortalidad γ | adimensional | 0.4 | 0.05 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Presas iniciales | adimensional | 4.0 | 0.05 a 15 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Depredadores iniciales | adimensional | 2.0 | 0.05 a 15 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Perturbación inicial δ | adimensional | 1e-05 | 1e-08 a 0.01 | Desplazamiento de la primera variable; en SIR transfiere δ de S a I conservando la población. |
| Inicio del tramo final / T | adimensional | 0.5 | 0 a 0.9 | Fracción de tiempo descartada en fase y barrido. SIR usa todo el intervalo para buscar el pico de I. |
| Barrido: α mínimo | adimensional | 0.5 | 0.05 a 3 | Inicio del barrido independiente. |
| Barrido: α máximo | adimensional | 2.0 | 0.05 a 3 | Final del barrido independiente. |
| Valores en el barrido | adimensional | 12 | 4 a 50 | Cada valor empieza desde la misma condición inicial. |

### Supuestos

- Variables y tiempo adimensionales; modelo determinista reducido.
- La distancia entre trayectorias no es un exponente de Lyapunov.
- El barrido muestra extremos muestreados a tiempo finito; no prueba una bifurcación asintótica.
- Sin capacidad de carga, migración ni ruido demográfico.

### Preguntas para investigar

- Sitúa las poblaciones en el equilibrio y comprueba que permanecen constantes.
- ¿Qué ocurre al aumentar la mortalidad del depredador?

### Ecuaciones

Crecimiento y depredación de presas:

$$\dot{x}=\alpha x-\beta xy$$

Conversión y mortalidad de depredadores:

$$\dot{y}=\delta xy-\gamma y$$

Equilibrio de coexistencia:

$$(x_*,y_*)=(\gamma/\delta,\alpha/\beta)$$

Integral primera para x,y positivos:

$$H=\delta x-\gamma\ln x+\beta y-\alpha\ln y$$

### Ejemplos

- [Presa y depredador: ciclos](../examples/lv_cycles.json): Las poblaciones oscilan con desfase; la integral primera se conserva.
- [Presa y depredador: equilibrio](../examples/lv_equilibrium.json): x=γ/δ e y=α/β dan un estado estacionario.

### Referencias

- [Scholarpedia · sistemas dinámicos](http://www.scholarpedia.org/article/Dynamical_systems)
- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)

## 21. SIR: dinámica de poblaciones

**Área:** Caos y dinámica.

Fracciones susceptible, infectada y recuperada; conservación, umbral y barrido de contagio.

**Escena:** Espacio de estados (S, I, R): fracciones de población, no posiciones físicas.

**Duración:** 80.0 adimensional por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Tasa de infección β | adimensional | 0.35 | 0.01 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Tasa de recuperación γ | adimensional | 0.1 | 0.01 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Fracción susceptible inicial | adimensional | 0.99 | 0.01 a 1 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Fracción infectada inicial | adimensional | 0.01 | 0 a 0.99 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Perturbación inicial δ | adimensional | 1e-05 | 1e-08 a 0.01 | Desplazamiento de la primera variable; en SIR transfiere δ de S a I conservando la población. |
| Inicio del tramo final / T | adimensional | 0.5 | 0 a 0.9 | Fracción de tiempo descartada en fase y barrido. SIR usa todo el intervalo para buscar el pico de I. |
| Barrido: β mínimo | adimensional | 0.05 | 0.01 a 2 | Inicio del barrido independiente. |
| Barrido: β máximo | adimensional | 0.8 | 0.01 a 2 | Final del barrido independiente. |
| Valores en el barrido | adimensional | 12 | 4 a 50 | Cada valor empieza desde la misma condición inicial. |

### Supuestos

- Variables y tiempo adimensionales; modelo determinista reducido.
- La distancia entre trayectorias no es un exponente de Lyapunov.
- El barrido muestra extremos muestreados a tiempo finito; no prueba una bifurcación asintótica.
- Población cerrada homogénea; inmunidad permanente y tasas constantes.
- Modelo didáctico; no está calibrado para decisiones clínicas.

### Preguntas para investigar

- Compara β/γ por debajo y por encima de 1.
- ¿Cómo cambia el pico si aumenta la fracción recuperada inicial?

### Ecuaciones

Susceptibles:

$$\dot{S}=-\beta SI$$

Infectados:

$$\dot{I}=\beta SI-\gamma I$$

Recuperados y conservación:

$$\dot{R}=\gamma I,\quad S+I+R=1$$

Umbral efectivo de crecimiento:

$$\mathcal{R}_0=\beta/\gamma,\quad \dot{I}>0\ \Leftrightarrow\ \mathcal{R}_0S>1$$

### Ejemplos

- [SIR: crecimiento y recuperación](../examples/sir_wave.json): I crece mientras (β/γ)S>1; S+I+R permanece en uno.
- [SIR: bajo el umbral](../examples/sir_below.json): Con β/γ<1 la fracción infectada decrece desde el inicio.

### Referencias

- [Kermack y McKendrick (1927)](https://doi.org/10.1098/rspa.1927.0118)
- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)

## 22. Mapa de Hénon

**Área:** Caos y dinámica.

Mapa discreto bidimensional: atractor, sensibilidad y barrido de a con detección de escapes.

**Escena:** Espacio ampliado (x, y, n). n es el índice de iteración. El análisis descarta el transitorio configurado.

**Variable de salida:** iteración. No se impone una duración temporal.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Parámetro a | adimensional | 1.4 | 0.5 a 1.5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Parámetro b | adimensional | 0.3 | 0 a 0.4 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Estado inicial x | adimensional | 0.1 | -0.5 a 0.5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Estado inicial y | adimensional | 0.1 | -0.5 a 0.5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Iteraciones | adimensional | 1600 | 200 a 5000 | Longitud de la órbita del mapa elegida para análisis. |
| Transitorio a descartar | adimensional | 300 | 0 a 4500 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Perturbación inicial δ | adimensional | 1e-05 | 1e-08 a 0.01 | Desplazamiento de la primera variable; en SIR transfiere δ de S a I conservando la población. |
| Barrido: a mínimo | adimensional | 1.0 | 0.5 a 1.5 | Inicio del barrido independiente. |
| Barrido: a máximo | adimensional | 1.4 | 0.5 a 1.5 | Final del barrido independiente. |
| Valores en el barrido | adimensional | 12 | 4 a 50 | Cada valor empieza desde la misma condición inicial. |

### Supuestos

- Variables y tiempo adimensionales; modelo determinista reducido.
- La distancia entre trayectorias no es un exponente de Lyapunov.
- El barrido muestra extremos muestreados a tiempo finito; no prueba una bifurcación asintótica.
- Iteración directa en float64; las órbitas que superan |estado|=10⁶ se declaran escapadas.

### Preguntas para investigar

- Compara a=1 y a=1.4.
- ¿Cómo cambia el atractor al modificar b?

### Ecuaciones

Mapa en x:

$$x_{n+1}=1-ax_n^2+y_n$$

Mapa en y:

$$y_{n+1}=bx_n$$

Contracción de área para |b|<1:

$$\det J=-b$$

Sensibilidad; no es un exponente asintótico:

$$d_n=\|\mathbf{u}_{n,\delta}-\mathbf{u}_n\|_2$$

### Ejemplos

- [Hénon: atractor clásico](../examples/henon_attractor.json): Tras descartar el transitorio aparece una estructura contraída en el plano.
- [Hénon: otro régimen](../examples/henon_periodic.json): Compara los puntos finales con a=1.4 usando el mismo estado inicial.

### Referencias

- [Hénon (1976)](https://doi.org/10.1007/BF01608556)

## 23. Kuramoto: sincronización colectiva

**Área:** Caos y dinámica.

Osciladores de fase acoplados: animación circular, parámetro de orden y barrido de sincronización.

**Escena:** Cada marcador es una fase sobre el círculo unitario: (cos θ, sin θ, 0). No son partículas materiales.

**Duración:** 15.0 adimensional por defecto; rango 0.5 a 120.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Número de osciladores | adimensional | 24 | 3 a 80 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Frecuencia natural media | adimensional | 1.0 | -3 a 3 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Desviación de frecuencia | adimensional | 0.4 | 0 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Acoplamiento K | adimensional | 2.0 | 0 a 6 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Perturbación inicial δ | adimensional | 1e-05 | 1e-08 a 0.01 | Desplazamiento de la primera variable; en SIR transfiere δ de S a I conservando la población. |
| Inicio del tramo final / T | adimensional | 0.5 | 0 a 0.9 | Fracción de tiempo descartada en fase y barrido. SIR usa todo el intervalo para buscar el pico de I. |
| Barrido: K mínimo | adimensional | 0.0 | 0 a 6 | Inicio del barrido independiente. |
| Barrido: K máximo | adimensional | 4.0 | 0 a 6 | Final del barrido independiente. |
| Valores en el barrido | adimensional | 12 | 4 a 50 | Cada valor empieza desde la misma condición inicial. |

### Supuestos

- Variables y tiempo adimensionales; modelo determinista reducido.
- La distancia entre trayectorias no es un exponente de Lyapunov.
- El barrido muestra extremos muestreados a tiempo finito; no prueba una bifurcación asintótica.
- Acoplamiento global y frecuencias normales fijas determinadas por la semilla.
- El orden mide coherencia instantánea; una población finita fluctúa incluso sin acoplamiento.

### Preguntas para investigar

- Compara K=0 y K=3 usando la misma semilla.
- ¿Cómo cambia la sincronización al ampliar la dispersión de frecuencias?

### Ecuaciones

Modelo global de fases:

$$\dot{\theta}_i=\omega_i+\frac{K}{N}\sum_j\sin(\theta_j-\theta_i)$$

Parámetro de orden complejo:

$$Z=\frac{1}{N}\sum_j e^{i\theta_j}=Re^{i\psi}$$

R=1: coherencia total de fases:

$$0\leq R\leq 1$$

Forma de campo medio usada en el cálculo:

$$\dot{\theta}_i=\omega_i+KR\sin(\psi-\theta_i)$$

### Ejemplos

- [Kuramoto: sincronización](../examples/kuramoto_sync.json): Con acoplamiento fuerte aumenta R y se agrupan las fases.
- [Kuramoto: osciladores libres](../examples/kuramoto_free.json): Con K=0 cada fase avanza a su frecuencia natural; R fluctúa.

### Referencias

- [Kuramoto · Scholarpedia](http://www.scholarpedia.org/article/Kuramoto_model)
- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)

## 24. Dispersión Compton 3D

**Área:** Simuladores de partículas.

Fotón sobre electrón libre: retroceso relativista, cuatro-momento y sección eficaz de Klein–Nishina.

**Escena:** Evento en t=0. Azul: fotón; ámbar: electrón. Fotón incidente hacia +Z; después se muestran el fotón dispersado y el electrón de retroceso. Las líneas son trayectorias libres fuera del evento.

**Duración:** 2.0 ns por defecto; rango 0.1 a 20.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Energía del fotón incidente | MeV | 0.5 | 0.001 a 10 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Ángulo polar de dispersión | ° | 60.0 | 0 a 180 | Ángulo de la hija 1 en el marco de reposo respecto a la dirección del boost +Z. |
| Azimut de dispersión | ° | 30.0 | -180 a 180 | Azimut de la hija 1 en el marco de reposo; la hija 2 lleva momento opuesto. |

### Supuestos

- Electrón libre inicialmente en reposo; un solo evento de dispersión.
- Fotón no polarizado; no hay electrones ligados, múltiples dispersiones ni creación de pares.

### Preguntas para investigar

- Compara 0°, 90° y 180°: ¿cuánta energía gana el electrón?
- Comprueba la conservación de energía y momento con la tabla de cuatro-momentos.

### Ecuaciones

Energía del fotón dispersado:

$$E^\prime=E/[1+(E/m_ec^2)(1-\cos\theta)]$$

Energía cinética del electrón:

$$K_e=E-E^\prime$$

Momento de retroceso:

$$\mathbf{p}_e=\mathbf{p}_\gamma-\mathbf{p}_\gamma^\prime$$

Klein–Nishina; k=E′/E, fotón no polarizado:

$$\frac{d\sigma}{d\Omega}=\frac{r_e^2}{2}k^2(k+k^{-1}-\sin^2\theta)$$

### Ejemplos

- [Compton: dispersión a 90°](../examples/compton_right.json): El fotón pierde energía y el electrón retrocede conservando cuatro-momento.
- [Compton: retrodispersión](../examples/compton_back.json): A 180° la transferencia de energía al electrón es máxima para esa energía incidente.

### Referencias

- [OpenStax · Relatividad y cuántica](https://openstax.org/details/books/university-physics-volume-3)
- [NIST · constantes CODATA](https://physics.nist.gov/cuu/Constants/)

## 25. Trampa de Paul: campo RF 3D

**Área:** Simuladores de partículas.

Confinamiento cuadrupolar ideal, micromovimiento, ecuaciones de Mathieu y trabajo de la fuente.

**Escena:** Posición en unidades reducidas. Es un campo cuadrupolar ideal; no se dibujan electrodos ni colisiones.

**Duración:** 30.0 uT por defecto; rango 0.5 a 80.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Coeficiente estático a | adimensional | 0.0 | -0.4 a 0.4 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Coeficiente RF q | adimensional | 0.25 | 0 a 1.2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Frecuencia RF Ω | rad/uT | 3.0 | 0.2 a 12 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Posición inicial x | uL | 1.0 | -3 a 3 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Posición inicial y | uL | 0.6 | -3 a 3 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Posición inicial z | uL | 0.4 | -3 a 3 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Velocidad inicial x | uL/uT | 0.0 | -2 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Velocidad inicial y | uL/uT | 0.0 | -2 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Velocidad inicial z | uL/uT | 0.0 | -2 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |

### Supuestos

- Coeficientes (ax,ay,az)=a(1,1,−2) y (qx,qy,qz)=q(1,1,−2), compatibles con Laplace.
- Unidades reducidas; a y q incorporan carga, masa, voltajes y escala geométrica.
- Acotación a tiempo finito no demuestra estabilidad asintótica. La fuente RF realiza trabajo.

### Preguntas para investigar

- Compara q=0.25 y q=0.8; observa los distintos ejes.
- Aumenta puntos de salida y compara el residuo de trabajo con la diferencia refinada del integrador.

### Ecuaciones

Ecuaciones de Mathieu:

$$\ddot{x}_i+\frac{\Omega^2}{4}[a_i-2q_i\cos(\Omega t)]x_i=0$$

Potencial cuadrupolar específico:

$$U/m=\frac{\Omega^2}{8}\sum_i[a_i-2q_i\cos(\Omega t)]x_i^2$$

Condición de Laplace:

$$\sum_i a_i=\sum_i q_i=0$$

Trabajo de la fuente; energía específica variable:

$$E(t)-E(0)=\int_0^t\partial_t U\,dt$$

### Ejemplos

- [Paul: micromovimiento confinado](../examples/paul_confined.json): Los ejes muestran movimiento lento y RF superpuestos en este intervalo.
- [Paul: sin campo](../examples/paul_free.json): Con a=q=0 se recupera movimiento rectilíneo uniforme.

### Referencias

- [Nobel · Paul y las trampas de iones](https://www.nobelprize.org/prizes/physics/1989/paul/lecture/)
- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)

## 26. Superficies paramétricas 3D

**Área:** Geometría 3D.

Esfera, toro, banda de Möbius y paraboloide hiperbólico; malla, área y comparación de resolución.

**Escena:** Malla geométrica en unidades de longitud reducidas. El cursor recorre una fila paramétrica, sin significado de tiempo físico.

**Variable de salida:** parámetro. No se impone una duración temporal.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Superficie | adimensional | Toro | Esfera, Toro, Banda de Möbius, Paraboloide hiperbólico | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Radio / escala R | uL | 1.5 | 0.2 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Radio menor / semianchura r | uL | 0.45 | 0.02 a 2 | Afecta al toro o a Möbius, no a esfera/paraboloide. |
| Coeficiente del paraboloide | 1/uL | 0.5 | -2 a 2 | Solo paraboloide: z=κ(x²−y²). |
| Muestras por parámetro | adimensional | 49 | 17 a 97 | La comparación usa 2N−1 muestras por eje. |

### Supuestos

- Área estimada por triangulación de la malla; no es un área exacta.
- Las costuras repiten vértices; Möbius identifica extremos invirtiendo el parámetro transversal.

### Preguntas para investigar

- Compara el área de esfera/toro con la referencia analítica.
- ¿Cómo cambia la diferencia de área al duplicar aproximadamente la resolución?
- Observa cómo se cierra Möbius con media vuelta.

### Ecuaciones

Superficie paramétrica:

$$\mathbf{r}=\mathbf{r}(u,v)$$

Área de una parametrización regular:

$$A=\int\!\int |\partial_u\mathbf{r}\times\partial_v\mathbf{r}|\,du\,dv$$

Referencia de esfera:

$$A_{\rm esfera}=4\pi R^2$$

Referencia de toro regular:

$$A_{\rm toro}=4\pi^2Rr,\quad R>r$$

### Ejemplos

- [Toro: área y resolución](../examples/surface_torus.json): El área triangulada se aproxima a 4π²Rr.
- [Esfera: área analítica](../examples/surface_sphere.json): El área de la malla se aproxima a 4πR².
- [Möbius: media vuelta](../examples/surface_mobius.json): La banda se cierra invirtiendo el parámetro transversal.
- [Paraboloide: curvaturas opuestas](../examples/surface_saddle.json): Las secciones x y y se curvan en sentidos contrarios.

### Referencias

- [MathWorld · geometría diferencial](https://mathworld.wolfram.com/DifferentialGeometry.html)

## 27. Geodésicas sobre una esfera

**Área:** Geometría 3D.

Círculo máximo por latitud, longitud y rumbo; arco, cuerda y restricción esférica.

**Escena:** Trayectoria analítica sobre la esfera. El arco puede dar varias vueltas y dejar de ser el camino mínimo entre extremos.

**Duración:** 12.0 uT por defecto; rango 0.5 a 80.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Radio de esfera R | uL | 1.5 | 0.1 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Latitud inicial | ° | 20.0 | -89 a 89 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Longitud inicial | ° | -40.0 | -180 a 180 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Rumbo desde el norte | ° | 65.0 | -180 a 180 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Rapidez angular | rad/uT | 0.4 | 0.01 a 3 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |

### Supuestos

- Esfera ideal de radio constante y velocidad angular uniforme.
- La curva es una geodésica; solo arcos de ángulo ≤ π minimizan entre sus extremos.

### Preguntas para investigar

- Compara longitud de arco y cuerda tras media vuelta.
- Cambia el rumbo inicial y observa distintos círculos máximos.

### Ecuaciones

Base ortonormal de posición y tangente inicial:

$$\mathbf{r}(t)=R[\mathbf{n}_0\cos\omega t+\mathbf{v}_0\sin\omega t]$$

Aceleración normal: geodésica:

$$|\mathbf{r}|=R,\quad \ddot{\mathbf{r}}=-\omega^2\mathbf{r}$$

Arco acumulado:

$$s=R\omega t$$

Cuerda desde el punto inicial:

$$d=2R|\sin(\omega t/2)|$$

### Ejemplos

- [Geodésica: rumbo oblicuo](../examples/geodesic_oblique.json): La trayectoria permanece en la esfera; compara arco y cuerda.
- [Geodésica: vuelta por el ecuador](../examples/geodesic_equator.json): Con latitud 0 y rumbo 90° la curva permanece en el ecuador.

### Referencias

- [MathWorld · geometría diferencial](https://mathworld.wolfram.com/DifferentialGeometry.html)

## 28. Grafos 3D: conectividad y rutas

**Área:** Grafos y redes.

Cuatro topologías reproducibles, grados, componentes, agrupamiento, Laplaciano y rutas mínimas.

**Escena:** Nodos y aristas de un grafo abstracto; la ruta amarilla usa los costes elegidos. El cursor visita sus nodos. Cruces de aristas no crean conexiones.

**Variable de salida:** paso de ruta. No se impone una duración temporal.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Número de nodos | adimensional | 32 | 6 a 80 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Topología | adimensional | Mundo pequeño | Mundo pequeño, Erdős–Rényi, Grafo geométrico, Retícula 3D | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Pesos de la red | adimensional | Unitarios | Unitarios, Longitud: coste / resistencia | Coste reducido c=ℓ/uL; pesos para difusión y oscilaciones = 1/c. En modo unitario ambos valen 1. |
| Probabilidad de enlace / reconexión | adimensional | 0.15 | 0 a 1 | Erdős–Rényi: probabilidad de cada arista. Mundo pequeño: probabilidad de reconectar. |
| Vecinos por lado en el anillo | adimensional | 2 | 1 a 6 | Solo mundo pequeño; requiere 2k < N. |
| Radio de enlace geométrico | uL | 0.9 | 0.1 a 3.5 | Solo grafo geométrico; conecta pares más cercanos que el radio. |
| Nodo de origen / excitación | desde 1 | 1 | 1 a 80 | Nodo que inicia ruta, calor o desplazamiento. |
| Destino (0 = último nodo) | adimensional | 0 | 0 a 80 | Solo rutas; no modifica el grafo. |

### Supuestos

- Grafo simple no dirigido, sin autoaristas, con semilla reproducible.
- Las intersecciones de líneas no crean nodos. Las coordenadas son una incrustación 3D.
- Las redes desconectadas se conservan; no se añaden enlaces para forzar una ruta.

### Preguntas para investigar

- Compara coste por número de aristas y por longitud.
- Usa Erdős–Rényi con p=0: ¿por qué no existe una ruta entre nodos distintos?

### Ecuaciones

Grado no ponderado:

$$d_i=\sum_j A_{ij}$$

Laplaciano simétrico ponderado:

$$L=D_W-W$$

Agrupamiento local; cero si di<2:

$$C_i=(A^3)_{ii}/[d_i(d_i-1)]$$

Dijkstra minimiza coste de ruta, no distancia en pantalla:

$$\ell(P)=\sum_{(i,j)\in P}c_{ij}$$

### Ejemplos

- [Grafo: atajos y ruta mínima](../examples/graph_small_world.json): Las reconexiones cambian rutas y agrupamiento manteniendo el número de aristas.
- [Grafo: nodos aislados](../examples/graph_disconnected.json): Con p=0 cada nodo es una componente y no hay ruta entre nodos distintos.

### Referencias

- [SciPy · grafos dispersos](https://docs.scipy.org/doc/scipy/reference/sparse.csgraph.html)

## 29. Difusión sobre grafos

**Área:** Grafos y redes.

Difusión continua y conservativa, evolución por color y equilibrio por componentes.

**Escena:** Color = cantidad difundida, con escala fija durante la reproducción. Las aristas son conexiones de intercambio, no tuberías físicas.

**Duración:** 8.0 uT por defecto; rango 0.1 a 80.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Número de nodos | adimensional | 32 | 6 a 80 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Topología | adimensional | Mundo pequeño | Mundo pequeño, Erdős–Rényi, Grafo geométrico, Retícula 3D | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Pesos de la red | adimensional | Unitarios | Unitarios, Longitud: coste / resistencia | Coste reducido c=ℓ/uL; pesos para difusión y oscilaciones = 1/c. En modo unitario ambos valen 1. |
| Probabilidad de enlace / reconexión | adimensional | 0.15 | 0 a 1 | Erdős–Rényi: probabilidad de cada arista. Mundo pequeño: probabilidad de reconectar. |
| Vecinos por lado en el anillo | adimensional | 2 | 1 a 6 | Solo mundo pequeño; requiere 2k < N. |
| Radio de enlace geométrico | uL | 0.9 | 0.1 a 3.5 | Solo grafo geométrico; conecta pares más cercanos que el radio. |
| Nodo de origen / excitación | desde 1 | 1 | 1 a 80 | Nodo que inicia ruta, calor o desplazamiento. |
| Destino (0 = último nodo) | adimensional | 0 | 0 a 80 | Solo rutas; no modifica el grafo. |
| Tasa de difusión D | 1/uT | 0.6 | 0.01 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Cantidad inicial en origen | uH | 1.0 | 0.01 a 10 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |

### Supuestos

- Grafo simple no dirigido, sin autoaristas, con semilla reproducible.
- Las intersecciones de líneas no crean nodos. Las coordenadas son una incrustación 3D.
- Las redes desconectadas se conservan; no se añaden enlaces para forzar una ruta.
- Capacidad unitaria por nodo; cantidades en unidades abstractas uH.
- Cada componente tiene su propia media de equilibrio.

### Preguntas para investigar

- Verifica la conservación de la cantidad total.
- Compara una red conectada con nodos aislados.

### Ecuaciones

Difusión en la red:

$$\dot{\mathbf{T}}=-DL\mathbf{T}$$

Solución espectral del Laplaciano simétrico:

$$\mathbf{T}(t)=V e^{-Dt\Lambda}V^T\mathbf{T}(0)$$

Conservación de cantidad total:

$$\frac{d}{dt}\sum_i T_i=0$$

Media en cada componente conexa:

$$T_{i,\infty}=|C|^{-1}\sum_{j\in C}T_j(0),\ i\in C$$

### Ejemplos

- [Difusión: retícula 3D](../examples/graph_heat_grid.json): La cantidad inicial se distribuye conservando su suma.
- [Difusión: sin conexiones](../examples/graph_heat_isolated.json): Sin enlaces la cantidad permanece en el origen.

### Referencias

- [SciPy · grafos dispersos](https://docs.scipy.org/doc/scipy/reference/sparse.csgraph.html)

## 30. Red de osciladores y modos

**Área:** Grafos y redes.

Vibración escalar acoplada por el grafo, disipación, energía y frecuencias normales.

**Escena:** Cada nodo representa un oscilador escalar y se desplaza en Z para visualizar su amplitud. La conectividad se mantiene; las líneas no son resortes centrales geométricos.

**Duración:** 15.0 uT por defecto; rango 0.5 a 60.

| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |
| --- | --- | --- | --- | --- |
| Número de nodos | adimensional | 32 | 6 a 80 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Topología | adimensional | Mundo pequeño | Mundo pequeño, Erdős–Rényi, Grafo geométrico, Retícula 3D | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Pesos de la red | adimensional | Unitarios | Unitarios, Longitud: coste / resistencia | Coste reducido c=ℓ/uL; pesos para difusión y oscilaciones = 1/c. En modo unitario ambos valen 1. |
| Probabilidad de enlace / reconexión | adimensional | 0.15 | 0 a 1 | Erdős–Rényi: probabilidad de cada arista. Mundo pequeño: probabilidad de reconectar. |
| Vecinos por lado en el anillo | adimensional | 2 | 1 a 6 | Solo mundo pequeño; requiere 2k < N. |
| Radio de enlace geométrico | uL | 0.9 | 0.1 a 3.5 | Solo grafo geométrico; conecta pares más cercanos que el radio. |
| Nodo de origen / excitación | desde 1 | 1 | 1 a 80 | Nodo que inicia ruta, calor o desplazamiento. |
| Destino (0 = último nodo) | adimensional | 0 | 0 a 80 | Solo rutas; no modifica el grafo. |
| Masa por nodo m | uM | 1.0 | 0.1 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Rigidez al equilibrio k₀ | uM/uT² | 0.2 | 0 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Acoplamiento k | uM/uT² | 1.0 | 0.01 a 5 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Amortiguamiento b | uM/uT | 0.03 | 0 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |
| Desplazamiento inicial en origen | uL | 0.6 | 0.01 a 2 | Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas. |

### Supuestos

- Grafo simple no dirigido, sin autoaristas, con semilla reproducible.
- Las intersecciones de líneas no crean nodos. Las coordenadas son una incrustación 3D.
- Las redes desconectadas se conservan; no se añaden enlaces para forzar una ruta.
- Potencial cuadrático en diferencias de desplazamiento; masas iguales.
- Frecuencias modales calculadas sin amortiguamiento. uE=uM·uL²/uT².

### Preguntas para investigar

- Con b=0 comprueba la conservación de energía.
- ¿Cómo cambia el espectro al reconectar el anillo?

### Ecuaciones

Ecuación de la red escalar:

$$m\ddot{\mathbf{x}}+b\dot{\mathbf{x}}+(k_0 I+kL)\mathbf{x}=0$$

Energía de la red:

$$E=\frac{m}{2}\sum_i\dot{x}_i^2+\frac{k_0}{2}\sum_i x_i^2+\frac{k}{2}\mathbf{x}^TL\mathbf{x}$$

Disipación viscosa:

$$\dot{E}=-b\sum_i\dot{x}_i^2$$

Frecuencias normales sin amortiguamiento:

$$\omega_j=\sqrt{(k_0+k\lambda_j)/m}$$

### Ejemplos

- [Red: energía conservada](../examples/graph_waves_free.json): Con amortiguamiento nulo se conserva la energía.
- [Red: vibraciones disipativas](../examples/graph_waves_damped.json): La energía decrece por el amortiguamiento viscoso.

### Referencias

- [SciPy · grafos dispersos](https://docs.scipy.org/doc/scipy/reference/sparse.csgraph.html)
- [SciPy · solve_ivp y DOP853](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)

## Condiciones adicionales y lectura de diagnósticos

- **Escenarios 3D:** Compton es cinemática de un evento con electrón libre inicialmente en reposo. Paul usa un cuadrupolo de Mathieu ideal con energía variable por trabajo RF; su balance de trabajo depende del muestreo de salida.
- **Geometría:** el cursor de superficies recorre un parámetro, no tiempo físico. Áreas por triangulación con comparación de mallas. Las geodésicas pueden dar varias vueltas y solo arcos de ángulo ≤ π son mínimos entre extremos.
- **Grafos:** índices desde 1, destino 0 significa último nodo. Los cruces no crean nodos. Sin ruta, las distancias son NA en el conjunto auxiliar. Coste por longitud y peso de acoplamiento inverso; o ambos unitarios. La difusión conserva cantidad por componente y la vibración usa desplazamientos escalares, no resortes centrales geométricos.
- **Gas 3D:** hasta 96 esferas, radio < L/6 y volumen ocupado ≤ 8 %. El paso limita cada desplazamiento a 0.3r. Los contactos se corrigen tras el avance, con dos pasadas por pares; compara observables al reducir Δt. Presión = impulso acumulado/(6L²t). La energía conservada no garantiza exactitud de tiempos de choque.
- **N cuerpos:** hasta 128 partículas, potencial suavizado y fronteras abiertas. Se controla Δt·ω ≤ 0.5 con una escala conservadora de la fuerza. Conservación de energía, momento y momento angular; comparación de posiciones a Δt/2. No hay colisiones, fusiones ni radiación. Las unidades son reducidas y no hay conversión SI automática.
- **Sistemas ampliados:** Rössler, Van der Pol, Lotka–Volterra, SIR, Hénon y Kuramoto incluyen condiciones vecinas y barrido de un parámetro. Cada valor se inicia de forma independiente; los extremos son muestreados en un horizonte finito. Los escapes/fallos se marcan NaN en el CSV. La distancia de estados no es un exponente de Lyapunov.
- **SIR:** S₀+I₀ ≤ 1; la condición vecina transfiere δ de S a I. Se controla S+I+R=1. El barrido busca extremos de I en el intervalo completo.
- **Hénon:** al menos 50 iteraciones tras descartar el transitorio. La órbita principal o vecina falla si supera |estado|=10⁶; el barrido registra los valores escapados sin unirlos.
- **Kuramoto:** frecuencias normales fijas por semilla, acoplamiento global y fases sin envolver. R es coherencia, no probabilidad. La distancia vecina se calcula con diferencias angulares mínimas.
- **Campo E/B:** límite de 2000 unidades del reloj interno para mantener una simulación interactiva. Reduce campos o tiempo si se supera. No se calculan radiación, colisiones ni pérdida por decaimiento de la partícula seguida.
- **Rutherford:** K/(mc²) ≤ 0.05. La masa del blanco se considera infinita; A solo calcula un radio orientativo. Si el acercamiento llega al radio nuclear, el potencial puntual no basta para interpretar ese régimen.
- **Dos cuerpos:** M ≥ m₁+m₂ y boost γ ≤ 10⁶. Se usan componentes de cono de luz para reducir cancelación numérica; reconstruir masas como E²−p² a boosts grandes puede perder precisión. El barrido angular no asigna una probabilidad de emisión.
- **Decaimiento radiactivo:** el fondo integrado esperado se limita a 10¹² cuentas. Los intervalos de población son puntuales; al cambiar la resolución cambian los intervalos del detector.
- **Barrera:** se limita la opacidad máxima a κa ≤ 300 para representar amplitudes con float64. El panel avisa si falta resolución espacial de la onda. La densidad es relativa y el cursor recorre posición, no tiempo.
- **Mapa logístico:** debe quedar una órbita de al menos 50 iteraciones después del transitorio. El barrido de bifurcaciones usa 1000 iteraciones transitorias y conserva 100 por valor de r; la órbita seleccionada usa los valores configurados.
- **Órbitas:** el centro es puntual, sin superficie ni colisiones. La energía es específica (J/kg). El paso máximo corresponde a τ=t√(GM/a³); la duración se expresa en períodos.
- **Duffing:** la FFT usa la segunda mitad, quita la media y aplica ventana Hann. La sección estroboscópica usa interpolación lineal y descarta el primer 20 % del tiempo. Aumenta duración y resolución para investigar respuestas complejas.

## Guardar y exportar

Los proyectos v2 guardan parámetros completos, unidades implícitas del modelo, semilla, tolerancias, nombre, investigador/a, objetivo, fuentes y notas. Se importan también proyectos v1. Los datos principales y auxiliares se eligen en la sección Resultados; CSV exporta todas sus filas y un JSON asociado. Las figuras y fórmulas pueden guardarse en PNG.

Este archivo y los proyectos de ejemplo se regeneran con `python scripts/generate_manual.py`.
