"""Modelos adicionales: cálculos puros y especificaciones de visualización."""
import numpy as np
import pandas as pd
from scipy.constants import G, c, e, epsilon_0, hbar, m_e
from scipy.integrate import solve_ivp
from scipy.stats import binom

from catalog import MODELS
from particle_data import MEV_J, PARTICLES, relativistic_kinematics


def line(x, y, label='', **kwargs):
    return dict(x=np.asarray(x), y=np.asarray(y), label=label, **kwargs)


def chart(title, xlabel, ylabel, *series, **kwargs):
    return dict(title=title, xlabel=xlabel, ylabel=ylabel, series=list(series), **kwargs)


def scene(xyz, labels, title, **kwargs):
    return dict(xyz=np.asarray(xyz), labels=labels, title=title, **kwargs)


def metric(value, label, fmt='.5g'):
    return (format(float(value), fmt), label)


def numeric(rhs, initial, duration, settings, event=None):
    """DOP853 y referencia refinada sobre una malla de salida idéntica."""
    opts = dict(method='DOP853', rtol=settings.rtol, atol=settings.atol,
                max_step=settings.max_step)
    sol = solve_ivp(rhs, (0, duration), initial, dense_output=True, events=event, **opts)
    if not sol.success:
        raise ValueError('La integración no convergió: '+sol.message)
    end = float(sol.t[-1])
    if end <= 0:
        raise ValueError('El evento inicial impide avanzar la simulación.')
    t = np.linspace(0, end, settings.points)
    y = sol.sol(t).T
    ref = solve_ivp(rhs, (0, end), initial, t_eval=t, method='DOP853',
                    rtol=max(1e-13, settings.rtol/10), atol=max(1e-15, settings.atol/10),
                    max_step=settings.max_step/2)
    if not ref.success or ref.y.shape[1] != len(t) or not np.isfinite(y).all() or not np.isfinite(ref.y).all():
        raise ValueError('La integración refinada no convergió o produjo valores no finitos.')
    reference = ref.y.T
    scaled = float(np.max(np.abs(y-reference)/np.maximum(1, np.max(np.abs(reference), axis=0))))
    return t, y, reference, scaled


def packet(config, t, states, data, visual, charts, metrics, diagnostic, *, refined=None, **extra):
    return dict(t=t, states=states, refined=refined,
                extra=dict(data=data, visual=visual, charts=charts, metrics=metrics,
                           diagnostic=diagnostic, **extra))


def numeric_note(config, scaled, additional='', variables='las variables de estado indicadas'):
    s = config.solver
    return (f'<b>DOP853 · float64</b><br>rtol = {s.rtol:g}; atol = {s.atol:g}; paso máximo = {s.max_step:g}. '
            f'Diferencia normalizada con rtol/10, atol/10 y paso/2: <b>{scaled:.6g}</b>.<br>'
            f'La comparación se hace sobre {variables}, escalando cada componente por max(1, max|referencia|). '
            'Es un diagnóstico empírico, no una cota garantizada del error global. '+additional)


def energy_drift(energy):
    scale = max(float(np.max(np.abs(energy))), 1e-30)
    return float(np.max(np.abs(energy-energy[0]))/scale)


def validate_model(model, p, config):
    from particle_simulator import PARTICLE_MODELS, validate_particles
    from dynamic_systems import DYNAMIC_MODELS, validate_dynamics
    if model in PARTICLE_MODELS: validate_particles(model,p,config)
    if model in DYNAMIC_MODELS: validate_dynamics(model,p,config)
    if model == 'logistic' and (p['transient'] >= p['iterations']-50 or p['rmin'] >= p['rmax']):
        raise ValueError('Deja al menos 50 iteraciones tras el transitorio y usa r mínimo < r máximo.')
    if model == 'two_body' and p['parent_mass'] < p['daughter1']+p['daughter2']:
        raise ValueError('El decaimiento requiere M ≥ m₁ + m₂. A igualdad, el momento en reposo es cero.')
    if model == 'two_body' and 1+p['parent_kinetic']/p['parent_mass'] > 1e6:
        raise ValueError('Este cálculo float64 admite boosts γ ≤ 10⁶. Reduce la energía de la madre.')
    if model == 'em_particle':
        part = PARTICLES[p['species']]
        b = np.linalg.norm([p['bx'],p['by'],p['bz']])
        electric = 1000*np.linalg.norm([p['ex'],p['ey'],p['ez']])
        phase = max(abs(part.charge_e*e)*b/part.mass_kg,abs(part.charge_e*e)*electric/(part.mass_kg*c))*config.duration*1e-9
        if phase > 2000:
            raise ValueError('El intervalo incluye demasiadas escalas de campo. Reduce E, B o la duración (máximo 2000 unidades internas).')
    if model == 'rutherford' and p['energy']/PARTICLES[p['species']].mass_mev > .05:
        raise ValueError('Reduce K: este modelo clásico exige K/(mc²) ≤ 0.05.')
    if model == 'quantum_barrier':
        opacity = np.sqrt(2*m_e*p['effective_mass']*p['barrier']*e)/hbar*p['width']*1e-9
        if opacity > 300:
            raise ValueError('Barrera demasiado opaca para visualizar la amplitud con float64: reduce anchura, altura o masa (κa ≤ 300).')
    if model == 'radioactive' and p['background']*config.duration > 1e12:
        raise ValueError('El fondo total esperado supera 1e12 cuentas. Reduce el fondo o la duración.')


def pendulum(config, p):
    L, m, g = p['length'], p['mass'], p['gravity']
    initial = [np.deg2rad(p['angle']), p['omega0']]
    def rhs(t,y):
        return [y[1], -g/L*np.sin(y[0])-p['friction']*y[1]+p['drive']*np.cos(p['frequency']*t)]
    t,y,ref,diff = numeric(rhs,initial,config.duration,config.solver)
    x, z = L*np.sin(y[:,0]), -L*np.cos(y[:,0])
    xyz = np.column_stack([x,np.zeros_like(t),z])
    energy = .5*m*L*L*y[:,1]**2+m*g*L*(1-np.cos(y[:,0]))
    small = initial[0]*np.cos(np.sqrt(g/L)*t)+initial[1]/np.sqrt(g/L)*np.sin(np.sqrt(g/L)*t)
    data = pd.DataFrame(dict(t_s=t,theta_rad=y[:,0],omega_rad_s=y[:,1],x_m=x,z_m=z,energy_J=energy))
    links = np.stack([np.zeros_like(xyz),xyz],axis=1)
    return packet(config,t,y,data,scene(xyz,['x (m)','y (m)','z (m)'],'PÉNDULO · POSICIÓN ESPACIAL',linkage=links,origins=[[0,0,0]]),
        [chart('Ángulo y referencia de ángulo pequeño','Tiempo (s)','θ (rad)',line(t,y[:,0],'No lineal'),line(t,small,'Lineal, sin fricción ni fuerza',linestyle='--')),
         chart('Plano de fases','θ (rad)','ω (rad/s)',line(y[:,0],y[:,1])),
         chart('Energía mecánica','Tiempo (s)','E (J)',line(t,energy)),
         chart('Velocidad angular','Tiempo (s)','ω (rad/s)',line(t,y[:,1]))],
        [metric(2*np.pi*np.sqrt(L/g),'Período de ángulo pequeño · s'),metric(np.max(np.abs(y[:,0])),'Pico angular muestreado · rad'),
         metric(energy[-1],'Energía final · J'),metric(diff,'Diferencia refinada normalizada','.2e')],
        numeric_note(config,diff,'La curva lineal de referencia excluye amortiguamiento y forzamiento. Su diferencia no mide el error numérico.'),refined=ref,energy=energy)


def double_pendulum(config,p):
    m1,m2,L1,L2,g = [p[k] for k in ['m1','m2','l1','l2','gravity']]
    M11,M22 = (m1+m2)*L1*L1, m2*L2*L2
    def rhs(t,y):
        a,b,w1,w2 = y
        delta=a-b; cross=m2*L1*L2*np.cos(delta)
        f1=-m2*L1*L2*np.sin(delta)*w2*w2-(m1+m2)*g*L1*np.sin(a)
        f2=m2*L1*L2*np.sin(delta)*w1*w1-m2*g*L2*np.sin(b)
        determinant=M11*M22-cross*cross
        return [w1,w2,(M22*f1-cross*f2)/determinant,(M11*f2-cross*f1)/determinant]
    initial=[np.deg2rad(p['theta1']),np.deg2rad(p['theta2']),p['w1'],p['w2']]
    t,y,ref,diff=numeric(rhs,initial,config.duration,config.solver)
    a,b,w1,w2=y.T
    first=np.column_stack([L1*np.sin(a),np.zeros_like(t),-L1*np.cos(a)])
    second=first+np.column_stack([L2*np.sin(b),np.zeros_like(t),-L2*np.cos(b)])
    K=.5*M11*w1*w1+.5*M22*w2*w2+m2*L1*L2*np.cos(a-b)*w1*w2
    U=-(m1+m2)*g*L1*np.cos(a)-m2*g*L2*np.cos(b)
    energy=K+U
    # La escala de deriva no depende de la elección del cero de potencial.
    scale=(m1+m2)*g*L1+m2*g*L2+np.max(K)
    drift=float(np.max(np.abs(energy-energy[0]))/scale)
    data=pd.DataFrame(dict(t_s=t,theta1_rad=a,theta2_rad=b,omega1_rad_s=w1,omega2_rad_s=w2,
                           x1_m=first[:,0],z1_m=first[:,2],x2_m=second[:,0],z2_m=second[:,2],energy_J=energy))
    visual=scene(second,['x (m)','y (m)','z (m)'],'PÉNDULO DOBLE · DOS MASAS',tracks=[dict(xyz=first,label='Masa 1')],
                 linkage=np.stack([np.zeros_like(first),first,second],axis=1),origins=[[0,0,0]])
    return packet(config,t,y,data,visual,
        [chart('Ángulos','Tiempo (s)','rad',line(t,a,'θ₁'),line(t,b,'θ₂')),
         chart('Energía total','Tiempo (s)','E (J)',line(t,energy)),
         chart('Plano de fases 1','θ₁ (rad)','ω₁ (rad/s)',line(a,w1)),
         chart('Plano de fases 2','θ₂ (rad)','ω₂ (rad/s)',line(b,w2))],
        [metric(energy[0],'Energía inicial · J'),metric(drift,'Deriva de energía normalizada','.2e'),
         metric(np.max(np.abs(w2)),'Pico |ω₂| · rad/s'),metric(diff,'Diferencia refinada normalizada','.2e')],
        numeric_note(config,diff,f'Deriva energética = max|E−E₀| / [(m₁+m₂)gL₁+m₂gL₂+max K] = {drift:.4g}. La sensibilidad puede amplificar diferencias a tiempos largos.'),refined=ref,energy=energy)


def projectile(config,p):
    az,el=np.deg2rad([p['azimuth'],p['elevation']])
    velocity=p['speed']*np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
    initial=np.r_[0.,0.,p['height'],velocity]
    wind=np.array([p['wind_x'],p['wind_y'],p['wind_z']])
    drag=.5*p['density']*p['cd']*p['area']/p['mass']
    def rhs(t,y):
        rel=y[3:]-wind
        return np.r_[y[3:],np.array([0.,0.,-p['gravity']])-drag*np.linalg.norm(rel)*rel]
    def ground(t,y):
        return y[2]
    ground.terminal=True;ground.direction=-1
    t,y,ref,diff=numeric(rhs,initial,config.duration,config.solver,ground)
    energy=.5*p['mass']*np.sum(y[:,3:]**2,axis=1)+p['mass']*p['gravity']*y[:,2]
    vacuum=initial[:3]+t[:,None]*velocity+np.column_stack([0*t,0*t,-.5*p['gravity']*t*t])
    analytic_error=float(np.max(np.linalg.norm(y[:,:3]-vacuum,axis=1))) if drag==0 else None
    data=pd.DataFrame(y,columns=['x_m','y_m','z_m','vx_m_s','vy_m_s','vz_m_s']);data.insert(0,'t_s',t);data['energy_J']=energy
    hit=abs(y[-1,2])<1e-6
    note=f'Suelo: {"alcanzado" if hit else "no alcanzado en el intervalo"}. '
    if analytic_error is not None:note+=f'Diferencia máxima frente a la parábola analítica: {analytic_error:.5g} m.'
    return packet(config,t,y,data,scene(y[:,:3],['x (m)','y (m)','Altura z (m)'],'PROYECTIL · VIENTO Y ARRASTRE'),
        [chart('Altura','Tiempo (s)','z (m)',line(t,y[:,2])),chart('Rapidez','Tiempo (s)','m/s',line(t,np.linalg.norm(y[:,3:],axis=1))),
         chart('Proyección horizontal','x (m)','y (m)',line(y[:,0],y[:,1])),chart('Energía mecánica','Tiempo (s)','J',line(t,energy))],
        [metric(t[-1],'Duración calculada · s'),metric(np.linalg.norm(y[-1,:2]),'Desplazamiento horizontal final · m'),
         metric(np.max(y[:,2]),'Altura máxima muestreada · m'),metric(diff,'Diferencia refinada normalizada','.2e')],
        numeric_note(config,diff,note),refined=ref,energy=energy,ground_hit=hit,analytic_error=analytic_error)


def orbit(config,p):
    mu=G*p['central_mass'];a=p['semimajor']*1000;ecc=p['eccentricity']
    period=2*np.pi*np.sqrt(a**3/mu);time_scale=np.sqrt(a**3/mu)
    # r/a y v/(a/time_scale); el reloj interno es t/time_scale.
    initial=[1-ecc,0.,0.,0.,np.sqrt((1+ecc)/(1-ecc)),0.]
    def rhs(t,y):
        radius=np.linalg.norm(y[:3]);return np.r_[y[3:],-y[:3]/radius**3]
    tau,y,ref,diff=numeric(rhs,initial,config.duration*2*np.pi,config.solver)
    t=tau*time_scale
    angle=np.deg2rad(p['inclination'])
    rotation=np.array([[1,0,0],[0,np.cos(angle),-np.sin(angle)],[0,np.sin(angle),np.cos(angle)]])
    pos=y[:,:3]@rotation.T*a;vel=y[:,3:]@rotation.T*a/time_scale
    radius=np.linalg.norm(pos,axis=1);speed=np.linalg.norm(vel,axis=1)
    energy=.5*speed**2-mu/radius; angular=np.linalg.norm(np.cross(pos,vel),axis=1)
    drift=energy_drift(energy);h_drift=energy_drift(angular)
    data=pd.DataFrame(dict(t_s=t,t_periods=t/period,x_m=pos[:,0],y_m=pos[:,1],z_m=pos[:,2],
        vx_m_s=vel[:,0],vy_m_s=vel[:,1],vz_m_s=vel[:,2],radius_m=radius,specific_energy_J_kg=energy,specific_angular_m2_s=angular))
    return packet(config,t,y,data,scene(pos/1000,['x (km)','y (km)','z (km)'],'ÓRBITA NEWTONIANA',origins=[[0,0,0]]),
        [chart('Radio orbital','Tiempo / período','r (km)',line(t/period,radius/1000)),
         chart('Rapidez','Tiempo / período','km/s',line(t/period,speed/1000)),
         chart('Deriva de energía','Tiempo / período','(ε−ε₀)/|ε₀|',line(t/period,(energy-energy[0])/abs(energy[0]))),
         chart('Momento angular específico','Tiempo / período','m²/s',line(t/period,angular))],
        [metric(period,'Período kepleriano · s'),metric(drift,'Deriva relativa de energía','.2e'),metric(h_drift,'Deriva relativa de momento angular','.2e'),metric(diff,'Diferencia refinada normalizada','.2e')],
        numeric_note(config,diff,'Integración normalizada: r/a, v/√(GM/a), τ=t√(GM/a³). El paso máximo se aplica a τ; la duración de la interfaz está en períodos.',variables='r/a y v/√(GM/a)'),
        refined=ref,energy=energy,angular=angular,period=period)


def coupled(config,p):
    def rhs(t,y):
        x1,x2,v1,v2=y
        return [v1,v2,(-p['k1']*x1-p['kc']*(x1-x2)-p['friction']*v1)/p['m1'],
                (-p['k2']*x2-p['kc']*(x2-x1)-p['friction']*v2)/p['m2']]
    t,y,ref,diff=numeric(rhs,[p['x1'],p['x2'],p['v1'],p['v2']],config.duration,config.solver)
    x1,x2,v1,v2=y.T
    E1=.5*p['m1']*v1*v1+.5*p['k1']*x1*x1
    E2=.5*p['m2']*v2*v2+.5*p['k2']*x2*x2
    Ec=.5*p['kc']*(x1-x2)**2;energy=E1+E2+Ec
    data=pd.DataFrame(dict(t_s=t,x1_m=x1,x2_m=x2,v1_m_s=v1,v2_m_s=v2,E1_J=E1,E2_J=E2,coupling_J=Ec,total_J=energy))
    return packet(config,t,y,data,scene(np.column_stack([x1,x2,t]),['x₁ (m)','x₂ (m)','t (s)'],'OSCILADORES · ESPACIO DE ESTADOS'),
        [chart('Posiciones','Tiempo (s)','m',line(t,x1,'x₁'),line(t,x2,'x₂')),chart('Energías','Tiempo (s)','J',line(t,E1,'Masa 1'),line(t,E2,'Masa 2'),line(t,Ec,'Acoplamiento')),
         chart('Plano de estados','x₁ (m)','x₂ (m)',line(x1,x2)),chart('Energía total','Tiempo (s)','J',line(t,energy))],
        [metric(energy[0],'Energía inicial · J'),metric(energy[-1],'Energía final · J'),metric(np.max(np.abs(x2)),'Pico muestreado |x₂| · m'),metric(diff,'Diferencia refinada normalizada','.2e')],
        numeric_note(config,diff,'Las energías individuales excluyen el resorte de acoplamiento; la energía total incluye ese término.'),refined=ref,energy=energy)


def duffing(config,p):
    def rhs(t,y):return [y[1],p['force']*np.cos(p['frequency']*t)-p['friction']*y[1]-p['alpha']*y[0]-p['beta']*y[0]**3]
    t,y,ref,diff=numeric(rhs,[p['position'],p['velocity']],config.duration,config.solver)
    x,v=y.T;energy=.5*v*v+.5*p['alpha']*x*x+.25*p['beta']*x**4
    period=2*np.pi/p['frequency'];ts=np.arange(period,config.duration,period);ts=ts[ts>.2*config.duration]
    xp=np.interp(ts,t,x);vp=np.interp(ts,t,v)
    values=x[len(x)//2:];window=np.hanning(len(values));signal=(values-values.mean())*window
    freq=np.fft.rfftfreq(len(values),t[1]-t[0]);spectrum=2*np.abs(np.fft.rfft(signal))/max(window.sum(),1)
    data=pd.DataFrame(dict(t=t,x=x,v=v,energy=energy))
    return packet(config,t,y,data,scene(np.column_stack([x,v,t]),['x','v','t'],'DUFFING · DINÁMICA NO LINEAL'),
        [chart('Posición','t','x',line(t,x)),chart('Espacio de fases','x','v',line(x,v)),
         chart('Sección estroboscópica (tras 20 %)','x','v',line(xp,vp,kind='scatter')),
         chart('FFT · segunda mitad, ventana Hann','Frecuencia (ciclos/t)','Amplitud',line(freq,spectrum))],
        [metric(period,'Período del forzamiento'),metric(np.max(np.abs(x)),'Pico |x| muestreado'),metric(len(ts),'Puntos estroboscópicos','.0f'),metric(diff,'Diferencia refinada normalizada','.2e')],
        numeric_note(config,diff,'La sección usa interpolación lineal sobre la salida: su precisión también depende del muestreo temporal. La FFT tiene resolución limitada por la duración.'),refined=ref,energy=energy,
        datasets={'Sección de Poincaré':pd.DataFrame(dict(t=ts,x=xp,v=vp)), 'Espectro FFT':pd.DataFrame(dict(frequency=freq,amplitude=spectrum))})


def logistic(config,p):
    n=p['iterations'];xs=np.empty(n+1);xs[0]=p['initial']
    for i in range(n):xs[i+1]=p['r']*xs[i]*(1-xs[i])
    valid=xs[p['transient']:-1]
    with np.errstate(divide='ignore'):
        local=np.log(np.abs(p['r']*(1-2*valid)))
    lyap=float(np.mean(local))
    rs=np.linspace(p['rmin'],p['rmax'],p['scan_points']);state=np.full_like(rs,p['initial'])
    kept=[]
    for i in range(1100):
        state=rs*state*(1-state)
        if i>=1000:kept.append(state.copy())
    scan=np.asarray(kept);rx=np.tile(rs,len(scan));ry=scan.ravel()
    grid=np.linspace(0,1,300);cobx=[xs[0]];coby=[0.]
    for i in range(min(80,n)):
        cobx.extend([xs[i],xs[i+1]]);coby.extend([xs[i+1],xs[i+1]])
    t=np.arange(n+1,dtype=float);data=pd.DataFrame(dict(iteration=t,x=xs))
    coords=np.column_stack([t,xs,np.r_[xs[1:],p['r']*xs[-1]*(1-xs[-1])]])
    finite_text='−∞' if np.isneginf(lyap) else f'{lyap:.5g}'
    return packet(config,t,xs[:,None],data,scene(coords,['n','xₙ','xₙ₊₁'],'MAPA LOGÍSTICO · ESTADOS DISCRETOS'),
        [chart('Órbita discreta','n','xₙ',line(t,xs)),chart('Mapa y cobweb (primeras 80 iteraciones)','xₙ','xₙ₊₁',line(grid,p['r']*grid*(1-grid),'f(x)'),line(grid,grid,'Identidad',linestyle='--'),line(cobx,coby,'Órbita')),
         chart('Bifurcaciones · 1000 transitorias','r','x',line(rx,ry,kind='scatter',size=.25)),
         chart('Estados tras el transitorio','x','Frecuencia',line(valid,valid,kind='hist'))],
        [metric(p['r'],'Parámetro r'),(finite_text,'Lyapunov finito · órbita seleccionada'),metric(n-p['transient'],'Iteraciones analizadas','.0f'),metric(p['scan_points'],'Valores r del barrido','.0f')],
        '<b>Mapa discreto · float64</b><br>Sin integrador diferencial. El exponente es la media de log|f′(x)| tras descartar el transitorio. '
        'Una derivada exactamente nula da −∞ en aritmética flotante. La gráfica de bifurcaciones descarta 1000 iteraciones y conserva 100 por cada r; '
        'la órbita elegida usa su propio transitorio configurable. No se certifica caos con una órbita finita.',lyapunov=lyap,
        datasets={'Bifurcaciones':pd.DataFrame(dict(r=rx,x=ry))})


def em_particle(config,p):
    part=PARTICLES[p['species']];mass=part.mass_kg;charge=part.charge_e*e
    E=1000*np.array([p['ex'],p['ey'],p['ez']]);B=np.array([p['bx'],p['by'],p['bz']])
    duration_s=config.duration*1e-9
    inverse_scale=max(abs(charge)*np.linalg.norm(B)/mass, abs(charge)*np.linalg.norm(E)/(mass*c),1/duration_s)
    scale=1/inverse_scale
    _,momentum,_=relativistic_kinematics(p['kinetic'],part.mass_mev)
    u_mag=momentum/part.mass_mev
    theta,phi=np.deg2rad([p['pitch'],p['azimuth']])
    direction=np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
    initial=np.r_[np.array([p['x'],p['y'],p['z']])*1e-3/(c*scale),u_mag*direction]
    electric=charge*scale/(mass*c)*E;magnetic=charge*scale/mass*B
    def rhs(t,y):
        u=y[3:];gamma=np.sqrt(1+np.dot(u,u));beta=u/gamma
        return np.r_[beta,electric+np.cross(beta,magnetic)]
    tau,y,ref,diff=numeric(rhs,initial,duration_s/scale,config.solver)
    t_s=tau*scale;position=y[:,:3]*c*scale;u=y[:,3:];u2=np.sum(u*u,axis=1)
    gamma=np.sqrt(1+u2);beta_vec=u/gamma[:,None];beta=np.linalg.norm(beta_vec,axis=1)
    # Evita cancelación de γ−1 a energía cinética pequeña.
    kinetic=part.mass_mev*u2/(gamma+1)
    momenta=u*part.mass_mev
    residual=(kinetic-kinetic[0])-charge*((position-position[0])@E)/MEV_J
    data=pd.DataFrame(dict(t_s=t_s,t_ns=t_s*1e9,x_m=position[:,0],y_m=position[:,1],z_m=position[:,2],
        px_MeV_c=momenta[:,0],py_MeV_c=momenta[:,1],pz_MeV_c=momenta[:,2],beta=beta,gamma=gamma,
        kinetic_MeV=kinetic,work_balance_MeV=residual))
    bnorm=np.linalg.norm(B)
    if bnorm>0:
        perpendicular=u[0]-np.dot(u[0],B/bnorm)*B/bnorm
        larmor=mass*c*np.linalg.norm(perpendicular)/(abs(charge)*bnorm)
        larmor_note=f'Radio de Larmor inicial respecto a B: {larmor:.6g} m. '
    else:larmor_note='B = 0: no hay radio de Larmor definido. '
    return packet(config,t_s,y,data,scene(position*1000,['x (mm)','y (mm)','z (mm)'],'LORENTZ RELATIVISTA · '+part.name.upper()),
        [chart('Energía cinética','Tiempo (ns)','K (MeV)',line(t_s*1e9,kinetic)),
         chart('Rapidez relativista','Tiempo (ns)','v/c',line(t_s*1e9,beta)),
         chart('Componentes del momento','Tiempo (ns)','MeV/c',line(t_s*1e9,momenta[:,0],'pₓ'),line(t_s*1e9,momenta[:,1],'pᵧ'),line(t_s*1e9,momenta[:,2],'p_z')),
         chart('Balance energía–trabajo eléctrico','Tiempo (ns)','ΔK − qE·Δr (MeV)',line(t_s*1e9,residual))],
        [metric(np.max(beta),'Rapidez máxima / c'),metric(gamma[-1],'Factor γ final'),metric(kinetic[-1],'Energía cinética final · MeV'),metric(diff,'Diferencia refinada normalizada','.2e')],
        numeric_note(config,diff,larmor_note+f'Máximo residuo de trabajo: {np.max(np.abs(residual)):.4g} MeV. Escala temporal interna: {scale:.6g} s. Sin radiación ni colisiones.',variables='r/(c·escala) y p/(mc)'),
        refined=ref,beta=beta,kinetic=kinetic,momentum=momenta,work_residual=residual,particle=part)


def rutherford(config,p):
    part=PARTICLES[p['species']];mass=part.mass_kg
    energy=p['energy']*MEV_J;b=p['impact']*1e-15
    kappa=part.charge_e*p['target_z']*e*e/(4*np.pi*epsilon_0)
    a=kappa/(2*energy);ecc=np.sqrt(1+(b/a)**2)
    u=np.linspace(-p['span'],p['span'],config.solver.points)
    factor=np.sqrt(mass*a**3/kappa)
    t=factor*(ecc*np.sinh(u)+u);t=t-t[0]
    x=a*(ecc+np.cosh(u));y=a*np.sqrt(ecc*ecc-1)*np.sinh(u)
    dtdu=factor*(ecc*np.cosh(u)+1)
    vx=a*np.sinh(u)/dtdu;vy=a*np.sqrt(ecc*ecc-1)*np.cosh(u)/dtdu
    angle=np.deg2rad(p['inclination'])
    position=np.column_stack([x,y*np.cos(angle),y*np.sin(angle)])
    velocity=np.column_stack([vx,vy*np.cos(angle),vy*np.sin(angle)])
    radius=np.linalg.norm(position,axis=1)
    total=.5*mass*(vx*vx+vy*vy)+kappa/radius
    angle_scatter=2*np.arctan(a/b)
    closest=a+np.sqrt(a*a+b*b);nuclear=1.2*p['target_a']**(1/3)*1e-15
    angles=np.deg2rad(np.linspace(2,178,config.solver.points))
    cross=(kappa/(4*energy))**2/np.sin(angles/2)**4/1e-30
    data=pd.DataFrame(dict(t_s=t,x_m=position[:,0],y_m=position[:,1],z_m=position[:,2],vx_m_s=velocity[:,0],vy_m_s=velocity[:,1],vz_m_s=velocity[:,2],r_m=radius,total_energy_MeV=total/MEV_J))
    note=('La distancia mínima calculada entra en el radio nuclear estimado: el modelo de Coulomb puntual es insuficiente para interpretar ese régimen. '
          if closest<nuclear else 'La distancia mínima supera el radio nuclear aproximado; siguen vigentes los supuestos de blanco fijo y potencial sin apantallamiento. ')
    drift=float(np.max(np.abs(total-energy))/energy)
    return packet(config,t,np.column_stack([position,velocity]),data,
        scene(position/1e-15,['x (fm)','y (fm)','z (fm)'],'RUTHERFORD · COULOMB REPULSIVO',origins=[[0,0,0]]),
        [chart('Distancia al blanco','Tiempo (s)','r (fm)',line(t,radius/1e-15)),
         chart('Energía cinética y potencial','Tiempo (s)','MeV',line(t,(total-kappa/radius)/MEV_J,'Cinética'),line(t,kappa/radius/MEV_J,'Potencial')),
         chart('Sección eficaz diferencial','θ (°)','fm²/sr',line(np.rad2deg(angles),cross),yscale='log'),
         chart('Proyección del plano de dispersión','X (fm)','Y (fm)',line(x/1e-15,y/1e-15))],
        [metric(np.rad2deg(angle_scatter),'Ángulo asintótico · °'),metric(closest/1e-15,'Distancia mínima analítica · fm'),metric(nuclear/1e-15,'Radio nuclear orientativo · fm'),metric(drift,'Residuo de energía / K incidente','.2e')],
        '<b>Solución hiperbólica analítica · float64</b><br>'+note+f'Residuo de energía frente a K incidente: {drift:.5g}. '
        'El ángulo indicado es asintótico; los extremos dibujados están a distancia finita. La masa A del blanco no introduce recoil ni tamaño en el potencial.',
        energy=total,scattering_angle=angle_scatter,closest=closest,nuclear_radius=nuclear,
        datasets={'Sección eficaz':pd.DataFrame(dict(theta_deg=np.rad2deg(angles),cross_section_fm2_sr=cross))})


def radioactive(config,p):
    rng=np.random.default_rng(config.seed);N=p['population'];rate=np.log(2)/p['half_life']
    t=np.linspace(0,config.duration,config.solver.points)
    lifetimes=rng.exponential(1/rate,N);ordered=np.sort(lifetimes)
    survivors=N-np.searchsorted(ordered,t,side='right')
    expected=N*np.exp(-rate*t);prob=expected/N
    low=binom.ppf(.025,N,prob);high=binom.ppf(.975,N,prob)
    events=np.histogram(lifetimes,bins=t)[0]
    dt=np.diff(t);detected=rng.binomial(events,p['efficiency'])+rng.poisson(p['background']*dt)
    expected_counts=p['efficiency']*N*(np.exp(-rate*t[:-1])-np.exp(-rate*t[1:]))+p['background']*dt
    activity=rate*expected
    data=pd.DataFrame(dict(t_s=t,survivors=survivors,expected_survivors=expected,low_95=low,high_95=high,expected_activity_s=activity))
    return packet(config,t,survivors[:,None],data,
        scene(np.column_stack([t,survivors,activity]),['t (s)','Supervivientes','Actividad esperada (s⁻¹)'],'DECAIMIENTO · OBSERVABLES DE POBLACIÓN'),
        [chart('Población y cuantiles puntuales','Tiempo (s)','N',line(t,survivors,'Realización'),line(t,expected,'Esperanza'),band=(t,low,high)),
         chart('Actividad esperada','Tiempo (s)','Decaimientos/s',line(t,activity)),
         chart('Cuentas por intervalo','Tiempo (s)','Cuentas',line(t[1:],detected,'Detectadas'),line(t[1:],expected_counts,'Esperanza')),
         chart('Tiempos de decaimiento dentro de T','Tiempo (s)','Eventos',line(lifetimes[lifetimes<=config.duration],lifetimes[lifetimes<=config.duration],kind='hist'))],
        [metric(1/rate,'Vida media τ · s'),metric(p['half_life'],'Semivida t½ · s'),metric(survivors[-1],'Supervivientes observados','.0f'),metric(detected.sum(),'Cuentas totales detectadas','.0f')],
        '<b>Exponenciales, binomial y Poisson · semilla '+str(config.seed)+'</b><br>'
        'La población esperada es analítica; los tiempos de cada evento y las detecciones son aleatorios y reproducibles. '
        'Los cuantiles binomiales tienen cobertura puntual discreta aproximada del 95 %, no describen una banda simultánea. '
        'Cambiar el número de puntos cambia el ancho de los intervalos del detector. Semivida y vida media son cantidades diferentes.',
        survivors=survivors,expected=expected,events=events,detected=detected,
        datasets={'Detector por intervalos':pd.DataFrame(dict(start_s=t[:-1],end_s=t[1:],decays=events,detected=detected,expected_counts=expected_counts))})


def two_body_kinematics(M,m1,m2,kinetic,theta,phi):
    values=np.asarray([M,m1,m2,kinetic,theta,phi],float)
    if not np.isfinite(values).all() or M<=0 or min(m1,m2,kinetic)<0 or M<m1+m2:
        raise ValueError('Masas o energía incompatibles con un decaimiento de dos cuerpos.')
    product=(M-m1-m2)*(M+m1+m2)*(M-m1+m2)*(M+m1-m2)
    rest_p=np.sqrt(max(0,product))/(2*M)
    E1=np.hypot(rest_p,m1);E2=np.hypot(rest_p,m2)
    # Caso M=m1+m2, uno de los cuales es cero: el producto de cuatro-momento sigue definido.
    theta,phi=np.deg2rad([theta,phi]);direction=np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
    gamma=1+kinetic/M;gamma_beta=np.sqrt((gamma-1)*(gamma+1));beta=gamma_beta/gamma
    def boost(energy,pvec,mass):
        if energy == 0:return np.zeros(4)
        transverse_mass2=mass*mass+pvec[0]**2+pvec[1]**2
        if pvec[2]>=0:
            plus=energy+pvec[2];minus=transverse_mass2/plus
        else:
            minus=energy-pvec[2];plus=transverse_mass2/minus
        # Componentes de cono de luz: evita restar E y |p_z| casi iguales.
        factor=gamma+gamma_beta
        plus*=factor;minus/=factor
        return np.array([.5*(plus+minus),pvec[0],pvec[1],.5*(plus-minus)])
    first=boost(E1,rest_p*direction,m1);second=boost(E2,-rest_p*direction,m2)
    parent=np.array([M+kinetic,0,0,np.sqrt(kinetic*(kinetic+2*M))])
    return parent,first,second,rest_p,gamma,beta


def two_body(config,p):
    parent,first,second,rest_p,gamma,beta=two_body_kinematics(p['parent_mass'],p['daughter1'],p['daughter2'],p['parent_kinetic'],p['theta'],p['phi'])
    t=np.linspace(0,config.duration*1e-9,config.solver.points)
    vel1=first[1:]/first[0]*c if first[0]>0 else np.zeros(3)
    vel2=second[1:]/second[0]*c if second[0]>0 else np.zeros(3)
    pos1=t[:,None]*vel1;pos2=t[:,None]*vel2
    cosines=np.linspace(-1,1,config.solver.points)
    E1star=np.hypot(rest_p,p['daughter1']);E2star=np.hypot(rest_p,p['daughter2'])
    scan1=gamma*(E1star+beta*rest_p*cosines);scan2=gamma*(E2star-beta*rest_p*cosines)
    residual=first+second-parent;abs_res=float(np.max(np.abs(residual)))
    rows=pd.DataFrame(np.vstack([parent,first,second]),columns=['energy_MeV','px_MeV_c','py_MeV_c','pz_MeV_c'])
    rows.insert(0,'object',['Madre','Hija 1','Hija 2']);rows['mass_MeV_c2']=[p['parent_mass'],p['daughter1'],p['daughter2']]
    energies=np.array([first[0],second[0]]);kinetics=energies-[p['daughter1'],p['daughter2']]
    angle1=np.rad2deg(np.arctan2(np.hypot(first[1],first[2]),first[3])) if np.linalg.norm(first[1:])>0 else 0.
    angle2=np.rad2deg(np.arctan2(np.hypot(second[1],second[2]),second[3])) if np.linalg.norm(second[1:])>0 else 0.
    visual=scene(pos1*100,['x (cm)','y (cm)','z (cm)'],'DOS CUERPOS · VUELO LIBRE DESDE EL VÉRTICE',
                 tracks=[dict(xyz=pos2*100,label='Hija 2',animate=True)],origins=[[0,0,0]])
    return packet(config,t,np.column_stack([pos1,pos2]),rows,visual,
        [chart('Energías lab según ángulo de emisión','cos θ*','E (MeV)',line(cosines,scan1,'Hija 1'),line(cosines,scan2,'Hija 2')),
         chart('Energía del evento','Hija','MeV',line([1,2],energies,'Total',kind='bar'),line([1,2],kinetics,'Cinética',kind='scatter')),
         chart('Proyección XZ del vuelo','z (cm)','x (cm)',line(pos1[:,2]*100,pos1[:,0]*100,'Hija 1'),line(pos2[:,2]*100,pos2[:,0]*100,'Hija 2')),
         chart('Residuo de conservación','Componente (E, px, py, pz)','MeV o MeV/c',line(np.arange(4),residual,kind='bar'))],
        [metric(rest_p,'Momento en reposo p* · MeV/c'),metric(gamma,'Boost γ de la madre'),metric(first[0],'Energía lab hija 1 · MeV'),metric(abs_res,'Residuo máx. cuatro-momento','.2e')],
        '<b>Cinemática analítica relativista · c = 1 para cuatro-momentos</b><br>'
        f'Residuo máximo de conservación: {abs_res:.6g} MeV o MeV/c. Ángulos lab respecto a +Z: {angle1:.6g}° y {angle2:.6g}°. '
        'El barrido angular no es una distribución de probabilidad: no se asigna elemento de matriz. '
        'Los cuatro-momentos son el resultado físico; las líneas de vuelo solo ilustran las velocidades después del evento. '
        'Un producto sin energía en el umbral tiene velocidad de visualización cero.',
        four_momenta=np.vstack([parent,first,second]),conservation_residual=residual,rest_momentum=rest_p,
        datasets={'Barrido angular':pd.DataFrame(dict(cos_theta_star=cosines,E1_lab_MeV=scan1,E2_lab_MeV=scan2)),
                  'Vuelo libre':pd.DataFrame(dict(t_s=t,x1_m=pos1[:,0],y1_m=pos1[:,1],z1_m=pos1[:,2],x2_m=pos2[:,0],y2_m=pos2[:,1],z2_m=pos2[:,2]))})


def barrier_amplitudes(energy_ev,barrier_ev,width_nm,mass_ratio=1.):
    if not np.isfinite([energy_ev,barrier_ev,width_nm,mass_ratio]).all() or energy_ev<=0 or barrier_ev<0 or width_nm<=0 or mass_ratio<=0:
        raise ValueError('Parámetros de barrera inválidos.')
    mass=m_e*mass_ratio;energy=energy_ev*e;potential=barrier_ev*e;width=width_nm*1e-9
    k=np.sqrt(2*mass*energy)/hbar
    q=np.sqrt(complex(2*mass*(energy-potential)))/hbar
    if abs(q*width)>350 and energy<potential:
        raise ValueError('La barrera excede el rango de amplitudes representable.')
    if abs(q*width)<1e-7:
        sin_over_q=width*(1-(q*width)**2/6)
        cosine=1-(q*width)**2/2
    else:
        sin_over_q=np.sin(q*width)/q;cosine=np.cos(q*width)
    denominator=cosine-1j*(k*k+q*q)/(2*k)*sin_over_q
    transmitted=np.exp(-1j*k*width)/denominator
    reflected=1j*(q*q-k*k)/(2*k)*sin_over_q/denominator
    return transmitted,reflected,k,q


def quantum_barrier(config,p):
    transmitted,reflected,k,q=barrier_amplitudes(p['energy'],p['barrier'],p['width'],p['effective_mass'])
    width=p['width']*1e-9;x=np.linspace(-3*width,4*width,config.solver.points)
    left=x<0;right=x>width;inside=~(left|right)
    psi=np.empty_like(x,dtype=complex)
    psi[left]=np.exp(1j*k*x[left])+reflected*np.exp(-1j*k*x[left]);psi[right]=transmitted*np.exp(1j*k*x[right])
    d=x[inside]-width
    if abs(q*width)<1e-7:
        sinc=d*(1-(q*d)**2/6)
    else:sinc=np.sin(q*d)/q
    psi[inside]=transmitted*np.exp(1j*k*width)*(np.cos(q*d)+1j*k*sinc)
    T=float(abs(transmitted)**2);R=float(abs(reflected)**2)
    scan=np.linspace(.001,p['scan_max'],config.solver.points)
    transmissions=np.array([abs(barrier_amplitudes(E,p['barrier'],p['width'],p['effective_mass'])[0])**2 for E in scan])
    potential=np.where((x>=0)&(x<=width),p['barrier'],0.)
    density=abs(psi)**2
    data=pd.DataFrame(dict(x_m=x,x_nm=x*1e9,psi_real=psi.real,psi_imag=psi.imag,density_relative=density,potential_eV=potential))
    needed=int(np.ceil(k*(x[-1]-x[0])*4/np.pi))+1
    sample_note=(f'El perfil puede estar submuestreado: para al menos 8 puntos por longitud de onda libre se estiman {needed} puntos. '
                 if needed>config.solver.points else 'El muestreo espacial resuelve al menos 8 puntos por longitud de onda libre. ')
    return packet(config,x*1e9,np.column_stack([psi.real,psi.imag]),data,
        scene(np.column_stack([x*1e9,psi.real,psi.imag]),['x (nm)','Re ψ','Im ψ'],'BARRERA 1D · ESPACIO COMPLEJO'),
        [chart('Potencial y energía incidente','x (nm)','eV',line(x*1e9,potential,'V(x)'),line(x*1e9,np.full_like(x,p['energy']),'E',linestyle='--')),
         chart('Densidad relativa','x (nm)','|ψ|²',line(x*1e9,density)),
         chart('Función de onda','x (nm)','Amplitud',line(x*1e9,psi.real,'Re ψ'),line(x*1e9,psi.imag,'Im ψ')),
         chart('Transmisión según energía','E (eV)','T',line(scan,transmissions))],
        [metric(T,'Coeficiente de transmisión T'),metric(R,'Coeficiente de reflexión R'),metric(abs(1-R-T),'Residuo |1−R−T|','.2e'),metric(2*np.pi/k*1e9,'Longitud de onda libre · nm')],
        '<b>Solución estacionaria analítica · amplitudes complejas float64</b><br>'
        f'Balance de flujo |1−R−T| = {abs(1-R-T):.6g}. '+sample_note+
        'La función de onda tiene amplitud incidente uno; |ψ|² es una densidad relativa, no una probabilidad normalizada en todo el espacio. '
        'El cursor recorre posición, no tiempo. Se usa el límite regular al llegar a E = V₀.',
        transmission=T,reflection=R,psi=psi,
        datasets={'Transmisión vs energía':pd.DataFrame(dict(energy_eV=scan,transmission=transmissions))})


RUNNERS={'pendulum':pendulum,'double_pendulum':double_pendulum,'projectile':projectile,'orbit':orbit,
         'coupled':coupled,'duffing':duffing,'logistic':logistic,'em_particle':em_particle,
         'rutherford':rutherford,'radioactive':radioactive,'two_body':two_body,'quantum_barrier':quantum_barrier}


def run_advanced(config):
    parameters=MODELS[config.model].values(config.parameters)
    validate_model(config.model,parameters,config)
    config.parameters=parameters
    from particle_simulator import PARTICLE_MODELS, run_particles
    from dynamic_systems import DYNAMIC_MODELS, run_dynamics
    if config.model in PARTICLE_MODELS:return run_particles(config,parameters)
    if config.model in DYNAMIC_MODELS:return run_dynamics(config,parameters)
    return RUNNERS[config.model](config,parameters)
