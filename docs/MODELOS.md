# Guía de modelos y ejemplos · DYNAMIS 2

Esta guía acompaña a las pestañas **Fórmulas y precisión**, **Datos** y **Modelos y ejemplos** del programa.
Incluye 15 modelos y 34 proyectos de ejemplo. El catálogo de referencia contiene 28 especies de partículas.

## Uso de las unidades y de la precisión

Los rangos de cada campo no garantizan que todas sus combinaciones sean válidas. La aplicación comprueba también condiciones conjuntas. Las figuras son espaciales, de estados o complejas según indique cada modelo. En escenas espaciales se aplica la misma escala a los tres ejes.

Las integraciones numéricas usan DOP853 y una segunda solución refinada. Las comparaciones de tolerancia no garantizan el error global. Los modelos analíticos conservan las limitaciones de float64 y del muestreo de salida.

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

## Condiciones adicionales y lectura de diagnósticos

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
