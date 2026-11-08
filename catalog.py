"""Catálogo declarativo: parámetros, unidades, supuestos y ejemplos del laboratorio."""
from dataclasses import dataclass, field
from numbers import Real, Integral
import math


@dataclass(frozen=True)
class Parameter:
    key: str
    label: str
    unit: str
    default: object
    low: float = 0.
    high: float = 1.
    step: float = .1
    integer: bool = False
    choices: tuple = ()
    help: str = ''

    def validate(self, value):
        if self.choices:
            if value not in dict(self.choices):
                raise ValueError(f'{self.label}: opción no reconocida.')
        elif (not isinstance(value, Real) or isinstance(value, bool)
              or not math.isfinite(value) or not self.low <= value <= self.high
              or (self.integer and not isinstance(value, Integral))):
            raise ValueError(f'{self.label}: debe estar entre {self.low:g} y {self.high:g} {self.unit}.')

    @property
    def caption(self):
        return self.label + (f' ({self.unit})' if self.unit else '')

    @property
    def description(self):
        return self.help or PARAMETER_HELP.get(self.key,'Parámetro de la ecuación; su unidad y dominio figuran en este campo y en las fórmulas.')


def P(key, label, unit, value, low, high, help='', step=.1, integer=False):
    return Parameter(key, label, unit, value, low, high, step, integer, help=help)


def Choice(key, label, default, choices, help=''):
    return Parameter(key, label, '', default, choices=tuple(choices), help=help)


PARAMETER_HELP = {
    'mass':'Masa inercial positiva; escala la energía y la respuesta a la fuerza.',
    'm1':'Masa inercial del primer cuerpo.','m2':'Masa inercial del segundo cuerpo.',
    'length':'Distancia entre el pivote y la masa puntual.',
    'l1':'Distancia del pivote fijo a la primera masa.','l2':'Distancia entre la primera y la segunda masa.',
    'gravity':'Magnitud constante de la aceleración gravitatoria; actúa hacia −Z.',
    'angle':'Desviación inicial respecto a la vertical inferior; se convierte de grados a radianes.',
    'theta1':'Ángulo de la primera varilla respecto a la vertical inferior.',
    'theta2':'Ángulo de la segunda varilla respecto a la vertical inferior.',
    'omega0':'Derivada temporal inicial del ángulo.','w1':'Velocidad angular inicial de la primera varilla.',
    'w2':'Velocidad angular inicial de la segunda varilla.',
    'friction':'Coeficiente disipativo; sus unidades dependen de la ecuación del modelo seleccionado.',
    'drive':'Amplitud de la aceleración angular externa A·cos(Ωt).',
    'frequency':'Frecuencia angular de la fuerza externa; un ciclo dura 2π/Ω.',
    'speed':'Magnitud de la velocidad inicial; elevación y azimut fijan sus componentes.',
    'elevation':'Ángulo de lanzamiento respecto al plano horizontal.',
    'azimuth':'Ángulo en XY, medido desde +X hacia +Y.',
    'height':'Altura inicial positiva sobre el suelo z = 0.',
    'density':'Densidad constante del aire; cero recupera el modelo sin arrastre.',
    'cd':'Coeficiente adimensional de arrastre cuadrático, supuesto constante.',
    'area':'Área frontal usada en la fuerza ρ·Cd·A·|v−w|·(v−w)/2.',
    'wind_x':'Componente X de la velocidad constante del aire.',
    'wind_y':'Componente Y de la velocidad constante del aire.',
    'wind_z':'Componente vertical de la velocidad constante del aire.',
    'central_mass':'Masa central fija que define μ = G·M; la masa orbitante es de prueba.',
    'semimajor':'Semieje mayor a; se convierte de kilómetros a metros.',
    'eccentricity':'Excentricidad de una órbita elíptica; cero es circular.',
    'inclination':'Rotación del plano orbital o de dispersión alrededor de X.',
    'k1':'Rigidez del resorte que une la primera masa a su equilibrio.',
    'k2':'Rigidez del resorte que une la segunda masa a su equilibrio.',
    'kc':'Rigidez del resorte que acopla ambas masas.',
    'x1':'Desplazamiento inicial de la primera masa desde el equilibrio.',
    'x2':'Desplazamiento inicial de la segunda masa desde el equilibrio.',
    'v1':'Velocidad inicial de la primera masa.','v2':'Velocidad inicial de la segunda masa.',
    'alpha':'Coeficiente de rigidez lineal de Duffing; negativo permite dos pozos de potencial.',
    'beta':'Rigidez cúbica positiva de Duffing, que limita el potencial a amplitudes grandes.',
    'force':'Amplitud del forzamiento armónico de Duffing.',
    'position':'Posición inicial adimensional.','velocity':'Velocidad inicial adimensional.',
    'r':'Parámetro de crecimiento del mapa logístico; 0 ≤ r ≤ 4 mantiene el intervalo [0,1].',
    'initial':'Estado inicial del mapa dentro del intervalo abierto (0,1).',
    'iterations':'Longitud de la órbita del mapa elegida para análisis.',
    'transient':'Iteraciones iniciales que se excluyen de la estimación de Lyapunov y del histograma.',
    'rmin':'Extremo inferior del barrido de bifurcaciones.',
    'rmax':'Extremo superior del barrido de bifurcaciones.',
    'scan_points':'Número de valores uniformemente espaciados del parámetro r.',
    'species':'Especie que fija la masa en reposo y la carga del proyectil; consulta el catálogo de partículas.',
    'kinetic':'Energía cinética inicial, excluyendo la energía de reposo mc².',
    'pitch':'Ángulo de la velocidad inicial respecto a +Z; no necesariamente respecto al vector B.',
    'ex':'Componente X del campo eléctrico uniforme; entrada en kV/m.',
    'ey':'Componente Y del campo eléctrico uniforme; entrada en kV/m.',
    'ez':'Componente Z del campo eléctrico uniforme; entrada en kV/m.',
    'bx':'Componente X del campo magnético uniforme en teslas.',
    'by':'Componente Y del campo magnético uniforme en teslas.',
    'bz':'Componente Z del campo magnético uniforme en teslas.',
    'x':'Posición espacial inicial X; entrada en milímetros.',
    'y':'Posición espacial inicial Y; entrada en milímetros.',
    'z':'Posición espacial inicial Z; entrada en milímetros.',
    'energy':'Energía cinética o energía incidente en las unidades indicadas; compara con las escalas del modelo.',
    'target_z':'Número de protones del blanco; su carga es Z·e.',
    'target_a':'Número másico usado solo para estimar 1.2·A^(1/3) fm; no introduce retroceso nuclear.',
    'impact':'Distancia perpendicular asintótica entre la trayectoria incidente y el centro del blanco.',
    'span':'Extremo del parámetro hiperbólico; amplía la ventana finita dibujada sin cambiar el ángulo asintótico.',
    'population':'Número de objetos inestables independientes al inicio.',
    'half_life':'Tiempo en el que la población esperada cae a la mitad; la vida media es t½/ln 2.',
    'efficiency':'Probabilidad de registrar cada decaimiento; no incluye tiempo muerto.',
    'background':'Tasa media de cuentas espurias de un proceso Poisson independiente.',
    'parent_mass':'Masa de la madre en reposo. Debe ser al menos la suma de las masas hijas.',
    'daughter1':'Masa en reposo de la primera hija; cero es la aproximación sin masa.',
    'daughter2':'Masa en reposo de la segunda hija; cero es la aproximación sin masa.',
    'parent_kinetic':'Energía cinética de la madre en laboratorio; el boost apunta hacia +Z.',
    'theta':'Ángulo de la hija 1 en el marco de reposo respecto a la dirección del boost +Z.',
    'phi':'Azimut de la hija 1 en el marco de reposo; la hija 2 lleva momento opuesto.',
    'barrier':'Altura constante del potencial rectangular entre x=0 y x=a; fuera, V=0.',
    'width':'Anchura a de la barrera rectangular; entrada en nanómetros.',
    'effective_mass':'Masa constante en la ecuación de Schrödinger, expresada como múltiplo de la masa del electrón.',
    'scan_max':'Extremo superior del barrido analítico de transmisión frente a energía.',
}


@dataclass(frozen=True)
class Model:
    name: str
    family: str
    summary: str
    parameters: tuple = ()
    numeric: bool = True
    time_unit: str = 's'
    duration: float = 25.
    time_range: tuple = (.5, 120.)
    timed: bool = True
    scene_note: str = ''
    assumptions: tuple = ()
    questions: tuple = ()
    formulas: tuple = ()
    references: tuple = ()

    def values(self, supplied):
        if not isinstance(supplied, dict):
            raise ValueError('Los parámetros del modelo deben ser un objeto JSON.')
        allowed = {p.key for p in self.parameters}
        if set(supplied)-allowed:
            raise ValueError('Parámetros desconocidos: '+', '.join(sorted(set(supplied)-allowed)))
        result = {}
        for p in self.parameters:
            result[p.key] = supplied.get(p.key, p.default)
            p.validate(result[p.key])
        return result


MECHANICS = ('OpenStax · Mecánica', 'https://openstax.org/details/books/university-physics-volume-1')
EM_REFERENCE = ('OpenStax · Electromagnetismo', 'https://openstax.org/details/books/university-physics-volume-2')
QUANTUM_REFERENCE = ('OpenStax · Relatividad y cuántica', 'https://openstax.org/details/books/university-physics-volume-3')
PDG_REFERENCE = ('Particle Data Group · tablas y revisiones', 'https://pdg.lbl.gov/')
SCIPY_REFERENCE = ('SciPy · solve_ivp y DOP853', 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html')
CODATA_REFERENCE = ('NIST · constantes CODATA', 'https://physics.nist.gov/cuu/Constants/')

MODELS = {
    'oscillator': Model('Oscilador amortiguado', 'Mecánica',
        'Movimiento lineal con disipación: posición, velocidad, energía y espacio de fases.',
        assumptions=('Resorte lineal ideal; masa puntual y amortiguamiento viscoso.', 'Variables en unidades SI.'),
        questions=('¿Cómo cambia el movimiento entre subamortiguado, crítico y sobreamortiguado?',), references=(MECHANICS, SCIPY_REFERENCE)),
    'lorenz': Model('Atractor de Lorenz', 'Caos y dinámica',
        'Tres ecuaciones no lineales para investigar sensibilidad a las condiciones iniciales.',
        time_unit='adimensional', assumptions=('Modelo reducido y adimensional; no es una predicción meteorológica.',
            'La separación entre dos trayectorias no equivale a un exponente de Lyapunov.'),
        questions=('Compara ρ = 10 y ρ = 28; observa los tiempos en los que las trayectorias se separan.',),
        references=(('Lorenz (1963)', 'https://doi.org/10.1175/1520-0469(1963)020%3C0130:DNF%3E2.0.CO;2'),)),
    'ensemble': Model('Conjunto probabilístico', 'Probabilidades',
        'Realizaciones reproducibles de un oscilador con rigidez y posición inicial inciertas.', numeric=False,
        assumptions=('K y X₀ son uniformes e independientes; c = 0.', 'Percentiles de realizaciones e intervalos de confianza tienen significados distintos.'),
        questions=('Mantén la semilla y compara N = 100, 1000 y 10000.', '¿Qué supuesto de independencia exige tu investigación?'),
        references=(('Wilson (1927)', 'https://doi.org/10.1080/01621459.1927.10502953'),)),
    'pendulum': Model('Péndulo no lineal', 'Mecánica',
        'Péndulo con amortiguamiento y excitación angular. Se compara la dinámica con el régimen de ángulo pequeño.',
        parameters=(P('length','Longitud L','m',1.,.05,10.,'Distancia del pivote a la masa.'),
            P('mass','Masa','kg',1.,.01,100.), P('gravity','Gravedad g','m/s²',9.80665,.01,30.),
            P('angle','Ángulo inicial','°',35.,-179.,179.), P('omega0','Velocidad angular inicial','rad/s',0.,-20.,20.),
            P('friction','Amortig. angular','s⁻¹',.03,0.,5.), P('drive','Excitación angular','rad/s²',0.,0.,20.),
            P('frequency','Frecuencia de excitación','rad/s',2.,.01,20.)),
        scene_note='Posición real del péndulo en el plano XZ; el eje Y es perpendicular al movimiento. La varilla sigue el instante seleccionado.',
        assumptions=('Masa puntual, varilla sin masa y pivote fijo.', 'El modelo incluye gravedad uniforme, rozamiento viscoso y un par externo prescrito.'),
        questions=('Compara 5° y 120°: ¿sigue siendo válido T ≈ 2π√(L/g)?', 'Con excitación cero, ¿cómo cambia la energía al aumentar el rozamiento?'),
        formulas=((r'$\ddot{\theta}+\eta\dot{\theta}+(g/L)\sin\theta=A\cos(\Omega t)$','Ecuación angular no lineal'),
            (r'$x=L\sin\theta,\quad z=-L\cos\theta$','Posición en el plano vertical'),
            (r'$E=\frac{1}{2} mL^2\dot{\theta}^2+mgL(1-\cos\theta)$','Energía referida al punto más bajo'),
            (r'$T_0=2\pi\sqrt{L/g}$','Período aproximado para ángulos pequeños')), references=(MECHANICS,)),
    'double_pendulum': Model('Péndulo doble', 'Caos y dinámica',
        'Dos péndulos acoplados con masas y longitudes independientes, energía y trayectorias de ambas masas.',
        parameters=(P('m1','Masa 1','kg',1.,.05,20.),P('m2','Masa 2','kg',1.,.05,20.),
            P('l1','Longitud 1','m',1.,.1,5.),P('l2','Longitud 2','m',1.,.1,5.),
            P('gravity','Gravedad','m/s²',9.80665,.1,30.),P('theta1','Ángulo 1 inicial','°',110.,-179.,179.),
            P('theta2','Ángulo 2 inicial','°',-20.,-179.,179.),P('w1','Velocidad angular 1','rad/s',0.,-15.,15.),
            P('w2','Velocidad angular 2','rad/s',0.,-15.,15.)), duration=15.,
        scene_note='Geometría física en el plano XZ. Las varillas enlazan el pivote, la masa 1 y la masa 2.',
        assumptions=('Varillas rígidas y sin masa; masas puntuales.', 'Sin fricción ni colisiones entre las masas o las varillas.'),
        questions=('Compara proyectos que difieran 0.01° en θ₁.', 'Reduce tolerancias y observa el balance de energía.'),
        formulas=((r'$\Delta=\theta_1-\theta_2,\quad M_{12}=m_2L_1L_2\cos\Delta$','Acoplamiento en la matriz de masas'),
            (r'$M_{11}=(m_1+m_2)L_1^2,\quad M_{22}=m_2L_2^2$','Elementos diagonales; se resuelve M·θ″ = f'),
            (r'$K=\frac{1}{2}M_{11}\dot{\theta}_1^2+\frac{1}{2}M_{22}\dot{\theta}_2^2+M_{12}\dot{\theta}_1\dot{\theta}_2$','Energía cinética acoplada'),
            (r'$U=-(m_1+m_2)gL_1\cos\theta_1-m_2gL_2\cos\theta_2$','Energía potencial; E = K + U')), references=(MECHANICS,)),
    'projectile': Model('Proyectil 3D con viento', 'Mecánica',
        'Lanzamiento tridimensional con gravedad, arrastre cuadrático, viento vectorial y evento de llegada al suelo.',
        parameters=(P('mass','Masa','kg',.145,.001,100.),P('speed','Rapidez inicial','m/s',35.,.01,500.),
            P('elevation','Elevación','°',40.,-80.,90.),P('azimuth','Azimut','°',20.,-180.,180.),
            P('height','Altura inicial','m',2.,.001,1000.),P('gravity','Gravedad','m/s²',9.80665,.01,30.),
            P('density','Densidad del aire','kg/m³',1.225,0.,10.),P('cd','Coeficiente Cd','',.47,0.,3.),
            P('area','Área frontal','m²',.0042,0.,2.),P('wind_x','Viento X','m/s',5.,-100.,100.),
            P('wind_y','Viento Y','m/s',0.,-100.,100.),P('wind_z','Viento Z','m/s',0.,-30.,30.)),duration=15.,
        scene_note='Trayectoria espacial real en metros. La simulación finaliza al cruzar el plano del suelo z = 0 o al alcanzar T.',
        assumptions=('Gravedad y viento uniformes; densidad y Cd constantes.', 'No incluye sustentación, rotación, rebotes ni variación atmosférica.'),
        questions=('Pon densidad = 0 y compara con el tiro parabólico analítico.', 'Invierte el viento lateral y compara el punto de impacto.'),
        formulas=((r'$\dot{\mathbf{r}}=\mathbf{v},\quad \mathbf{u}=\mathbf{v}-\mathbf{w}$','Velocidad relativa al viento'),
            (r'$m\dot{\mathbf{v}}=m\mathbf{g}-\frac{1}{2}\rho C_D A|\mathbf{u}|\mathbf{u}$','Gravedad y arrastre cuadrático'),
            (r'$z(t)=z_0+v_{z0}t-\frac{1}{2}gt^2\quad(\rho=0)$','Referencia de vacío'),
            (r'$E=\frac{1}{2}m|\mathbf{v}|^2+mgz$','Energía mecánica; el viento puede transferir energía')), references=(MECHANICS,)),
    'orbit': Model('Órbita gravitatoria', 'Mecánica',
        'Órbita de prueba alrededor de una masa central, con excentricidad e inclinación y diagnósticos de invariantes.',
        parameters=(P('central_mass','Masa central','kg',5.9722e24,1e10,1e32),P('semimajor','Semieje mayor','km',10000.,1.,1e9),
            P('eccentricity','Excentricidad','',.3,0.,.95),P('inclination','Inclinación','°',35.,0.,180.)),
        time_unit='períodos',duration=2.,time_range=(.1,20.),
        scene_note='Posición espacial en kilómetros. El punto de origen es la masa central; el eje temporal no forma parte de la geometría.',
        assumptions=('Partícula de prueba y campo newtoniano central; masa central fija.', 'Sin tamaño de los cuerpos, colisiones, relatividad, atmósfera ni perturbaciones.'),
        questions=('Para e = 0, verifica r constante y el período de Kepler.', 'Compara conservación de energía y momento angular al refinar el paso.'),
        formulas=((r'$\ddot{\mathbf{r}}=-GM\mathbf{r}/r^3$','Aceleración gravitatoria central'),
            (r'$T=2\pi\sqrt{a^3/(GM)}$','Período kepleriano'),
            (r'$\epsilon=|\mathbf{v}|^2/2-GM/r=-GM/(2a)$','Energía específica'),
            (r'$\mathbf{h}=\mathbf{r}\times\mathbf{v}$','Momento angular específico conservado')), references=(MECHANICS, CODATA_REFERENCE)),
    'coupled': Model('Osciladores acoplados', 'Mecánica',
        'Dos grados de libertad, resortes y amortiguamiento para observar batidos y transferencia de energía.',
        parameters=(P('m1','Masa 1','kg',1.,.05,20.),P('m2','Masa 2','kg',1.,.05,20.),
            P('k1','Rigidez 1','N/m',4.,.01,100.),P('k2','Rigidez 2','N/m',4.,.01,100.),
            P('kc','Acoplamiento','N/m',.8,0.,100.),P('friction','Amortiguamiento común','kg/s',0.,0.,10.),
            P('x1','Posición inicial 1','m',1.,-10.,10.),P('x2','Posición inicial 2','m',0.,-10.,10.),
            P('v1','Velocidad inicial 1','m/s',0.,-20.,20.),P('v2','Velocidad inicial 2','m/s',0.,-20.,20.)),duration=40.,
        scene_note='Espacio de estados (x₁, x₂, t): el tercer eje representa tiempo; no es una trayectoria espacial.',
        assumptions=('Resortes lineales; desplazamientos medidos desde el equilibrio.', 'Amortiguamiento viscoso igual en ambas masas.'),
        questions=('Con masas y resortes iguales, compara modos en fase y en oposición.', 'Excita solo la masa 1 y observa la transferencia de energía.'),
        formulas=((r'$m_1\ddot{x}_1=-k_1x_1-k_c(x_1-x_2)-c\dot{x}_1$','Primera masa'),
            (r'$m_2\ddot{x}_2=-k_2x_2-k_c(x_2-x_1)-c\dot{x}_2$','Segunda masa'),
            (r'$U=\frac{1}{2}k_1x_1^2+\frac{1}{2}k_2x_2^2+\frac{1}{2}k_c(x_1-x_2)^2$','Energía potencial total'),
            (r'$\omega_s=\sqrt{k/m},\quad\omega_a=\sqrt{(k+2k_c)/m}$','Modos normales para m₁=m₂ y k₁=k₂')), references=(MECHANICS,)),
    'duffing': Model('Oscilador de Duffing', 'Caos y dinámica',
        'Oscilador forzado no lineal con espacio de fases, sección estroboscópica y espectro de frecuencia.',
        parameters=(P('alpha','Coeficiente α','',-1.,-5.,10.),P('beta','Coeficiente β','',1.,.01,10.),
            P('friction','Amortiguamiento δ','',.2,0.,5.),P('force','Forzamiento γ','',.3,0.,5.),
            P('frequency','Frecuencia Ω','',1.2,.05,10.),P('position','Posición inicial','',.1,-10.,10.),
            P('velocity','Velocidad inicial','',0.,-10.,10.)),time_unit='adimensional',duration=100.,
        scene_note='Espacio de estados (x, v, t), con tiempo adimensional como tercer eje.',
        assumptions=('Modelo adimensional, forzamiento armónico y rigidez cúbica positiva.', 'FFT de la segunda mitad con ventana Hann; la resolución depende de la duración.'),
        questions=('Compara forzamientos 0.1 y 0.3.', 'Observa puntos cada período de la fuerza; pocos puntos no bastan para caracterizar el caos.'),
        formulas=((r'$\ddot{x}+\delta\dot{x}+\alpha x+\beta x^3=\gamma\cos(\Omega t)$','Ecuación de Duffing'),
            (r'$H=\frac{1}{2}v^2+\frac{1}{2}\alpha x^2+\frac{1}{4}\beta x^4$','Energía del sistema sin forzamiento ni disipación'),
            (r'$t_n=2\pi n/\Omega$','Sección estroboscópica'),
            (r'$X_k=\sum_n w_n(x_n-\bar x)e^{-2\pi i kn/N}$','Espectro FFT con ventana')), references=(SCIPY_REFERENCE,)),
    'logistic': Model('Mapa logístico y bifurcaciones', 'Caos y dinámica',
        'Iteración discreta, cobweb, exponente de Lyapunov de la órbita y barrido de bifurcaciones.', numeric=False, timed=False,
        parameters=(P('r','Parámetro r','',3.8,0.,4.),P('initial','Estado inicial','',.2,1e-8,1-1e-8),
            P('iterations','Iteraciones','',1200,300,5000,integer=True,step=100),
            P('transient','Descartar primeras','',300,0,4000,integer=True,step=100),
            P('rmin','r mínimo del barrido','',2.5,0.,4.),P('rmax','r máximo del barrido','',4.,0.,4.),
            P('scan_points','Valores r del barrido','',250,50,500,integer=True,step=50)),time_unit='iteración',
        scene_note='Coordenadas (n, xₙ, xₙ₊₁). La escena representa estados discretos, no posiciones espaciales.',
        assumptions=('Mapa matemático adimensional; aritmética float64.', 'El exponente se estima sobre una órbita finita después del transitorio.'),
        questions=('Compara r = 2.8, 3.2 y 4.', 'Aumenta el transitorio y la longitud de la órbita antes de concluir estabilidad.'),
        formulas=((r'$x_{n+1}=rx_n(1-x_n)$','Regla de evolución discreta'),
            (r'$f^{\prime}(x)=r(1-2x)$','Derivada local del mapa'),
            (r'$\lambda_N=\frac{1}{N}\sum_n\log|r(1-2x_n)|$','Estimación del exponente de Lyapunov'),
            (r'$x^*=0,\quad x^*=1-1/r$','Puntos fijos; el segundo requiere r > 0'))),
}

from particle_data import CHARGED_CHOICES

MODELS.update({
    'em_particle': Model('Partícula relativista en campos E/B', 'Partículas y cuántica',
        'Trayectoria de una partícula cargada en campos uniformes, con momento relativista, energía y rapidez.',
        parameters=(Choice('species','Partícula','electron',CHARGED_CHOICES),
            P('kinetic','Energía cinética inicial','MeV',.01,1e-6,100000.),
            P('pitch','Ángulo polar respecto a +Z','°',65.,0.,180.),P('azimuth','Azimut inicial','°',0.,-180.,180.),
            P('ex','Campo Eₓ','kV/m',0.,-1000.,1000.),P('ey','Campo Eᵧ','kV/m',0.,-1000.,1000.),
            P('ez','Campo E_z','kV/m',0.,-1000.,1000.),
            P('bx','Campo Bₓ','T',0.,-10.,10.),P('by','Campo Bᵧ','T',0.,-10.,10.),P('bz','Campo B_z','T',.02,-10.,10.),
            P('x','Posición X inicial','mm',0.,-1000.,1000.),P('y','Posición Y inicial','mm',0.,-1000.,1000.),
            P('z','Posición Z inicial','mm',0.,-1000.,1000.)),time_unit='ns',duration=5.,time_range=(.001,10000.),
        scene_note='Trayectoria espacial en milímetros. Se integra el momento relativista con variables normalizadas; el tiempo de salida se muestra en ns.',
        assumptions=('Partícula puntual y campos externos uniformes, sin colisiones, espín ni emisión de radiación.',
            'La trayectoria de muones se calcula sin eliminar partículas por decaimiento; usa el módulo de decaimiento para poblaciones.'),
        questions=('Invierte la carga eligiendo electrón y positrón: ¿cambia el sentido de giro?',
            'Con E = 0, verifica energía constante. Con B = 0 y E paralelo, verifica dp/dt = qE.'),
        formulas=((r'$\dot{\mathbf{r}}=\mathbf{p}/(\gamma m),\quad \gamma=\sqrt{1+|\mathbf{p}/(mc)|^2}$','Velocidad y factor relativista'),
            (r'$\dot{\mathbf{p}}=q(\mathbf{E}+\mathbf{v}\times\mathbf{B})$','Fuerza de Lorentz'),
            (r'$E^2=p^2c^2+m^2c^4,\quad K=(\gamma-1)mc^2$','Relación energía–momento'),
            (r'$\dot{E}=q\mathbf{E}\cdot\mathbf{v},\quad r_L=p_\perp/(|q|B)$','Trabajo eléctrico y radio de Larmor en campo magnético uniforme')),
        references=(EM_REFERENCE, QUANTUM_REFERENCE, CODATA_REFERENCE, PDG_REFERENCE)),
    'rutherford': Model('Dispersión de Rutherford', 'Partículas y cuántica',
        'Dispersión coulombiana repulsiva con trayectoria hiperbólica, ángulo asintótico y sección eficaz diferencial.', numeric=False, timed=False,
        parameters=(Choice('species','Proyectil','alpha',(('alpha','Partícula α'),('proton','Protón'))),
            P('energy','Energía cinética incidente','MeV',5.,.001,100.),P('target_z','Z del blanco','',79,1,92,integer=True,step=1),
            P('target_a','A del blanco (radio estimado)','',197,1,238,integer=True,step=1),
            P('impact','Parámetro de impacto b','fm',50.,.1,10000.),P('span','Extensión hiperbólica','',3.,1.,5.),
            P('inclination','Rotación del plano','°',25.,-180.,180.)),time_unit='s',
        scene_note='Trayectoria clásica en femtómetros alrededor de un blanco puntual fijo. El ángulo y la sección eficaz se refieren al régimen asintótico.',
        assumptions=('Blanco infinitamente pesado y puntual; interacción coulombiana repulsiva no relativista.',
            'Sin apantallamiento, fuerza nuclear, recoil, estructura del núcleo ni pérdida de energía.',
            'A solo estima el radio nuclear 1.2·A^(1/3) fm; no modifica el potencial.'),
        questions=('Duplica la energía o el impacto y compara el ángulo.', 'Compara la distancia mínima con el radio nuclear estimado antes de interpretar el resultado.'),
        formulas=((r'$\kappa=Z_1Z_2e^2/(4\pi\epsilon_0),\quad a=\kappa/(2K)$','Escala coulombiana de la órbita'),
            (r'$\theta=2\arctan(a/b)$','Ángulo de dispersión asintótico'),
            (r'$r_{\min}=a+\sqrt{a^2+b^2}$','Distancia mínima de acercamiento'),
            (r'$\frac{d\sigma}{d\Omega}=\left(\frac{\kappa}{4K}\right)^2\sin^{-4}(\theta/2)$','Sección eficaz diferencial, calculada en fm²/sr')),
        references=(QUANTUM_REFERENCE, CODATA_REFERENCE)),
    'radioactive': Model('Decaimiento radiactivo y detección', 'Partículas y cuántica',
        'Población estocástica de núcleos o partículas inestables, ley exponencial, eficiencia del detector y fondo.',
        numeric=False,time_unit='s',duration=50.,time_range=(1e-12,1e10),
        parameters=(P('population','Población inicial N₀','',10000,100,1000000,integer=True,step=1000),
            P('half_life','Semivida t½','s',10.,1e-12,1e10),P('efficiency','Eficiencia de detección','',.7,0.,1.,step=.05),
            P('background','Fondo de detección','cuentas/s',2.,0.,1e9)),
        scene_note='Espacio de observables (tiempo, supervivientes, actividad esperada). No representa posiciones de partículas individuales.',
        assumptions=('Decaimientos independientes con tasa constante, un solo canal efectivo y sin cadena de descendientes.',
            'Detección binomial independiente; fondo Poisson. No incluye tiempo muerto ni resolución energética.',
            'Bandas de supervivientes: cuantiles binomiales para cada tiempo, no banda simultánea.'),
        questions=('Compara t½ con la vida media τ = t½/ln 2.', 'Pon eficiencia = 1 y fondo = 0; luego observa el efecto del detector.'),
        formulas=((r'$\lambda=\ln 2/t_{1/2},\quad \tau=1/\lambda$','Constante de decaimiento y vida media'),
            (r'$\mathbb{E}[N(t)]=N_0e^{-\lambda t},\quad A(t)=\lambda N_0e^{-\lambda t}$','Supervivientes y actividad esperada'),
            (r'$N(t)\sim\operatorname{Binomial}(N_0,e^{-\lambda t})$','Distribución puntual de supervivientes'),
            (r'$C_i\sim\operatorname{Binomial}(D_i,\epsilon)+\operatorname{Poisson}(b\Delta t_i)$','Cuentas detectadas por intervalo')),
        references=(QUANTUM_REFERENCE, PDG_REFERENCE)),
    'two_body': Model('Decaimiento relativista de dos cuerpos', 'Partículas y cuántica',
        'Cinemática de un decaimiento M → 1 + 2: marcos de reposo y laboratorio, boost y conservación del cuatro-momento.',
        numeric=False,time_unit='ns',duration=1.,time_range=(.001,100.),
        parameters=(P('parent_mass','Masa de la madre M','MeV/c²',139.57039,.001,1e6),
            P('daughter1','Masa hija 1','MeV/c²',105.6583755,0.,1e6),P('daughter2','Masa hija 2','MeV/c²',0.,0.,1e6),
            P('parent_kinetic','Energía cinética de la madre','MeV',300.,0.,1e7),
            P('theta','Ángulo polar en reposo','°',65.,0.,180.),P('phi','Azimut en reposo','°',20.,-180.,180.)),
        scene_note='Esquema de vuelo libre en centímetros después de un vértice en el origen. Se muestran ambas hijas; no incluye un detector ni una distribución de canales.',
        assumptions=('Un único evento de dos cuerpos; c = 1 en los cuatro-momentos (MeV y MeV/c).',
            'Masas fijas, sin anchura, polarización, elementos de matriz ni interacciones posteriores.',
            'Los ejemplos con neutrino usan masa nula como aproximación cinemática.'),
        questions=('Carga π⁺ → μ⁺ν y compara madre en reposo y madre en movimiento.', 'Verifica que la suma de los cuatro-momentos de las hijas coincide con el de la madre.'),
        formulas=((r'$p^*=\frac{\sqrt{[M^2-(m_1+m_2)^2][M^2-(m_1-m_2)^2]}}{2M}$','Momento en el marco de reposo, c = 1'),
            (r'$E_i^*=\sqrt{(p^*)^2+m_i^2}$','Energías en reposo de la madre'),
            (r"$E'=\gamma(E+\beta p_z),\quad p_z'=\gamma(p_z+\beta E)$",'Boost a lo largo de +Z'),
            (r'$P_M^\mu=P_1^\mu+P_2^\mu,\quad E_i^2-|\mathbf{p}_i|^2=m_i^2$','Conservación y masas invariantes')),
        references=(PDG_REFERENCE, QUANTUM_REFERENCE)),
    'quantum_barrier': Model('Barrera cuántica 1D', 'Partículas y cuántica',
        'Estado estacionario sobre una barrera rectangular: función de onda compleja, densidad y coeficientes de transmisión y reflexión.',
        numeric=False,timed=False,time_unit='posición (nm)',
        parameters=(P('energy','Energía incidente','eV',2.,.001,100.),P('barrier','Altura de barrera','eV',5.,0.,100.),
            P('width','Anchura de barrera','nm',.4,.01,5.),P('effective_mass','Masa efectiva / mₑ','',1.,.01,10.),
            P('scan_max','Energía máxima del barrido','eV',12.,.01,200.)),
        scene_note='Representación (x, Re ψ, Im ψ) de una función de onda estacionaria. El eje x es espacial; las amplitudes complejas no son coordenadas de una trayectoria.',
        assumptions=('Ecuación de Schrödinger no relativista 1D; barrera rectangular y masa efectiva constante.',
            'Estado estacionario de flujo incidente unitario en amplitud: |ψ|² no está normalizada a una partícula.',
            'No modela colapso, evolución temporal de un paquete ni teoría cuántica de campos.'),
        questions=('Compara E < V₀, E = V₀ y E > V₀.', 'Busca resonancias de transmisión y verifica R + T = 1.'),
        formulas=((r'$-\frac{\hbar^2}{2m}\psi^{\prime\prime}+V(x)\psi=E\psi$','Ecuación estacionaria de Schrödinger'),
            (r'$k=\sqrt{2mE}/\hbar,\quad q=\sqrt{2m(E-V_0)}/\hbar$','Número de onda; q es imaginario bajo la barrera'),
            (r'$T=|t|^2,\quad R=|r|^2,\quad R+T=1$','Flujo conservado para potenciales iguales a ambos lados'),
            (r'$T(E=V_0)=[1+mV_0a^2/(2\hbar^2)]^{-1}$','Límite regular en la cima de la barrera')),
        references=(QUANTUM_REFERENCE, CODATA_REFERENCE)),
})

MODEL_NAMES = {key: model.name for key, model in MODELS.items()}


@dataclass(frozen=True)
class Example:
    key: str
    label: str
    model: str
    expected: str
    values: dict = field(default_factory=dict)
    parameters: dict = field(default_factory=dict)


EXAMPLES = (
    Example('spring_free','Energía conservada','oscillator','La energía permanece constante dentro del error numérico.',{'damping':0.,'duration':20.}),
    Example('spring_critical','Amortiguamiento crítico','oscillator','Con m = 1 y k = 4, c crítico = 4; no hay oscilación.',{'damping':4.,'duration':8.}),
    Example('lorenz_calm','Lorenz: equilibrio estable','lorenz','Para ρ = 10, las trayectorias tienden a uno de los equilibrios.',{'rho':10.,'duration':30.}),
    Example('lorenz_chaos','Lorenz: atractor clásico','lorenz','Para ρ = 28 aparecen las dos regiones del atractor y sensibilidad inicial.',{'rho':28.,'duration':30.}),
    Example('ensemble_small','Incertidumbre pequeña','ensemble','Compara la dispersión debida a K y a X₀; son fuentes independientes.',{'stiffness_std':.1,'position_std':.02,'damping':0.}),
    Example('ensemble_more','Probabilidad con 5000 realizaciones','ensemble','El intervalo Wilson cuantifica el error de muestreo; compara con N = 100.',{'count':5000,'damping':0.}),
    Example('pendulum_small','Péndulo de ángulo pequeño','pendulum','Período cercano a 2π√(L/g) y energía constante.',{'duration':12.},{'angle':5.,'friction':0.}),
    Example('pendulum_large','Péndulo de gran amplitud','pendulum','El período supera la aproximación de ángulo pequeño.',{'duration':20.},{'angle':120.,'friction':0.}),
    Example('double_chaos','Péndulo doble energético','double_pendulum','Movimiento complejo; conserva la energía aunque la trayectoria sea sensible.',{'duration':15.}),
    Example('double_small','Péndulo doble de baja amplitud','double_pendulum','Observa modos acoplados cerca del equilibrio.',{'duration':20.},{'theta1':5.,'theta2':5.}),
    Example('projectile_vacuum','Tiro parabólico en vacío','projectile','La trayectoria coincide con la parábola analítica hasta tocar el suelo.',{'duration':20.},{'density':0.,'azimuth':0.,'wind_x':0.}),
    Example('projectile_wind','Proyectil con viento cruzado','projectile','El arrastre y el viento lateral cambian el alcance y la desviación.',{'duration':15.},{'wind_x':-8.,'wind_y':10.}),
    Example('orbit_circle','Órbita circular','orbit','El radio es constante y una vuelta tarda un período.',{'duration':2.},{'eccentricity':0.}),
    Example('orbit_ellipse','Órbita elíptica inclinada','orbit','Mayor rapidez cerca del periastro; energía y momento angular conservados.',{'duration':2.},{'semimajor':20000.,'eccentricity':.65,'inclination':55.}),
    Example('coupled_beats','Batidos y transferencia','coupled','La excitación pasa de una masa a la otra.',{'duration':50.}),
    Example('coupled_mode','Modo simétrico','coupled','Ambas masas se mueven juntas y el resorte de acoplamiento no se deforma.',{'duration':20.},{'x1':1.,'x2':1.}),
    Example('duffing_periodic','Duffing: forzamiento débil','duffing','Compara la sección estroboscópica y el espectro con el caso de forzamiento mayor.',{'duration':100.},{'force':.1}),
    Example('duffing_nonlinear','Duffing: forzamiento no lineal','duffing','La respuesta puede cambiar mucho con las condiciones iniciales y el transitorio.',{'duration':120.},{'force':.3}),
    Example('logistic_fixed','Mapa: punto fijo','logistic','Con r = 2.8, la órbita converge a 1 − 1/r.',parameters={'r':2.8}),
    Example('logistic_chaos','Mapa: r = 4','logistic','Para una órbita típica, el exponente finito se acerca a ln 2.',parameters={'r':4.}),
    Example('electron_helix','Electrón: hélice magnética','em_particle','La rapidez y la energía se conservan; el campo magnético curva la trayectoria.',{'duration':5.}),
    Example('positron_helix','Positrón: giro opuesto','em_particle','Con las mismas condiciones, el signo de la carga invierte el sentido de giro.',{'duration':5.},{'species':'positron'}),
    Example('electric_acceleration','Protón: aceleración eléctrica','em_particle','Con B = 0, p_z crece linealmente y la rapidez permanece menor que c.',{'duration':100.},{'species':'proton','kinetic':.01,'pitch':0.,'ez':100.,'bz':0.}),
    Example('rutherford_gold','Alfa sobre oro','rutherford','Para 5 MeV y b = 50 fm, la dispersión asintótica es de unas decenas de grados.'),
    Example('rutherford_far','Rutherford: impacto lejano','rutherford','Al aumentar b, disminuye el ángulo de desviación.',parameters={'impact':200.}),
    Example('decay_population','Semivida de 10 s','radioactive','La población esperada queda en la mitad después de 10 s.',{'duration':50.}),
    Example('muon_lifetime','Población de muones en reposo','radioactive','Vida media τ ≈ 2.1969811 μs; la semivida es τ·ln 2.',{'duration':1e-5},{'half_life':2.1969811e-6*math.log(2),'efficiency':1.,'background':0.}),
    Example('pion_rest','π⁺ → μ⁺ + ν: madre en reposo','two_body','Las hijas tienen momentos opuestos de igual magnitud; neutrino tratado como sin masa.',parameters={'parent_kinetic':0.}),
    Example('pion_boost','π⁺ → μ⁺ + ν: laboratorio','two_body','El boost cambia energías y ángulos, conservando el cuatro-momento.'),
    Example('kaon_two_pions','K⁺ → π⁺ + π⁰','two_body','Ambas masas hijas son distintas; compara las energías en reposo y laboratorio.',parameters={'parent_mass':493.677,'daughter1':139.57039,'daughter2':134.9768,'parent_kinetic':500.}),
    Example('z_electrons','Z⁰ → e⁺ + e⁻','two_body','En reposo, las energías de las hijas son aproximadamente M_Z/2.',parameters={'parent_mass':91187.6,'daughter1':.51099895069,'daughter2':.51099895069,'parent_kinetic':0.}),
    Example('quantum_tunnel','Túnel: energía bajo la barrera','quantum_barrier','La transmisión es positiva aunque E < V₀, y R + T ≈ 1.'),
    Example('quantum_above','Energía sobre la barrera','quantum_barrier','La reflexión puede persistir por interferencia aunque E > V₀.',parameters={'energy':8.}),
    Example('quantum_top','Energía igual a la barrera','quantum_barrier','La solución usa el límite regular, sin dividir por q = 0.',parameters={'energy':5.}),
)
