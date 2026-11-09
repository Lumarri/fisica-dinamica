"""Simulaciones clásicas de muchas partículas y diagnósticos de conservación."""
import numpy as np
import pandas as pd
from advanced_models import packet, scene, chart, line, metric

PARTICLE_MODELS = {'gas_box', 'nbody'}


def validate_particles(model, p, config):
    n = p['bodies']
    steps = int(np.ceil(config.duration / p['step'])) + config.solver.points
    if steps*n*n > 100_000_000:
        raise ValueError('Demasiadas evaluaciones por pares. Reduce N o la duración, o aumenta el paso (límite: 10⁸).')
    if model == 'gas_box':
        fraction = n*4*np.pi*p['radius']**3/(3*p['box']**3)
        if p['radius'] >= p['box']/6 or fraction > .08:
            raise ValueError('Usa radio < lado/6 y fracción de volumen ≤ 8 % para el gas diluido.')
    strength = p.get('body_mass',1.) if p.get('interaction')=='gravity' else p.get('charge',0.)**2/p.get('body_mass',1.)
    if model == 'nbody' and p['step']*np.sqrt(p['coupling']*n*strength/p['softening']**3) > .5:
        raise ValueError('Paso demasiado grande para la fuerza suavizada. Reduce Δt o aumenta ε (criterio conservador Δt·ω ≤ 0.5).')


def nonoverlapping_positions(n, half, radius, rng):
    positions = []
    for _ in range(n):
        for attempt in range(10000):
            candidate = rng.uniform(-half, half, 3)
            if not positions or np.min(np.linalg.norm(np.asarray(positions)-candidate, axis=1)) > 2.05*radius:
                positions.append(candidate)
                break
        else:
            raise ValueError('No se pudo inicializar el gas sin solapamientos; reduce radio o cantidad.')
    return np.asarray(positions)


def elastic_pair(positions, velocities, i, j, radius):
    """Impulso normal entre masas iguales; devuelve si hubo choque entrante."""
    displacement = positions[i]-positions[j]
    distance = np.linalg.norm(displacement)
    if distance >= 2*radius:
        return False
    normal = displacement / distance if distance > 1e-14 else np.array([1., 0., 0.])
    approach = np.dot(velocities[i]-velocities[j], normal)
    collided = approach < 0
    if collided:
        velocities[i] -= approach*normal
        velocities[j] += approach*normal
    correction = .5*(2*radius-distance+1e-12)*normal
    positions[i] += correction
    positions[j] -= correction
    return bool(collided)


def reflect_walls(positions, velocities, half, mass):
    impulse = 0.
    vector = np.zeros(3)
    for axis in range(3):
        for sign in [-1, 1]:
            outside = sign*positions[:,axis] > half
            entering = outside & (sign*velocities[:,axis] > 0)
            change = -2*mass*velocities[entering,axis]
            impulse += np.sum(np.abs(change))
            vector[axis] -= np.sum(change)  # impulso recibido por el recipiente
            positions[outside,axis] = sign*(2*half-sign*positions[outside,axis])
            velocities[entering,axis] *= -1
    return float(impulse), vector


def particle_frames(t, positions, velocities, unit):
    frames, n, _ = positions.shape
    data = pd.DataFrame(dict(frame=np.repeat(np.arange(frames),n),
                             particle=np.tile(np.arange(1,n+1),frames)))
    clock='s' if unit=='m' else 'uT'
    data.insert(1,'t_'+clock,np.repeat(t,n))
    for j,axis in enumerate('xyz'):
        data[axis+'_'+unit] = positions[:,:,j].ravel()
        data['v'+axis+'_'+unit+'_'+clock] = velocities[:,:,j].ravel()
    return data


def gas_box(config, p):
    rng = np.random.default_rng(config.seed)
    n, L, radius, mass = p['bodies'],p['box'],p['radius'],p['body_mass']
    half = L/2-radius
    pos = nonoverlapping_positions(n,half,radius,rng)
    vel = rng.normal(size=(n,3));vel -= vel.mean(axis=0)
    vel *= p['rms_speed']/np.sqrt(np.mean(np.sum(vel**2,axis=1)))
    t = np.linspace(0,config.duration,config.solver.points)
    positions = np.empty((len(t),n,3));velocities = np.empty_like(positions)
    pressures = np.zeros(len(t));collisions = np.zeros(len(t),dtype=int)
    wall_vectors = np.zeros((len(t),3));steps=0;count=0;impulse=0.;wall_vector=np.zeros(3)
    ii,jj = np.triu_indices(n,1)
    positions[0],velocities[0] = pos,vel
    for frame in range(1,len(t)):
        remaining = t[frame]-t[frame-1]
        while remaining > 1e-13:
            dt = min(remaining,p['step'],.3*radius/max(np.max(np.linalg.norm(vel,axis=1)),1e-15))
            steps += 1
            if steps*n*n > 100_000_000:
                raise ValueError('El paso limitado por la rapidez supera el presupuesto. Reduce velocidad, N o duración.')
            pos += dt*vel
            for _ in range(2):
                wall,vector = reflect_walls(pos,vel,half,mass);impulse+=wall;wall_vector+=vector
                distances = np.linalg.norm(pos[ii]-pos[jj],axis=1)
                for i,j in zip(ii[distances<2*radius],jj[distances<2*radius]):
                    count += elastic_pair(pos,vel,i,j,radius)
            wall,vector=reflect_walls(pos,vel,half,mass);impulse+=wall;wall_vector+=vector
            remaining -= dt
        positions[frame],velocities[frame] = pos,vel
        pressures[frame] = impulse/(6*L*L*t[frame]);collisions[frame]=count;wall_vectors[frame]=wall_vector
    energy = .5*mass*np.sum(velocities**2,axis=(1,2))
    momentum = mass*np.sum(velocities,axis=1)
    balance = np.linalg.norm(momentum+wall_vectors-momentum[0],axis=1)
    drift = np.max(np.abs(energy-energy[0]))/max(energy[0],1e-30)
    ideal = 2*energy[0]/(3*L**3)
    data = pd.DataFrame(dict(t_s=t,kinetic_J=energy,collisions=collisions,wall_pressure_Pa=pressures,
                             dilute_reference_Pa=np.full(len(t),ideal),momentum_balance_kg_m_s=balance))
    speeds = np.linalg.norm(velocities[-1],axis=1)
    visual=scene(positions[:,0],['x (m)','y (m)','z (m)'],'GAS · ESFERAS ELÁSTICAS',
                 particles=positions,particle_colors=np.arange(n),box=L,physical=True,trail_count=5)
    note=(f'<b>Gas clásico · impulsos elásticos · float64</b><br>N = {n}; semilla = {config.seed}; '
          f'{steps} subpasos; Δt ≤ {p["step"]:g} s y desplazamiento ≤ 0.3r por subpaso. '
          f'Deriva relativa de K: {drift:.4g}; balance de impulso con paredes: {np.max(balance):.4g} kg·m/s.<br>'
          'Los contactos se detectan después del avance, con corrección de penetración y dos pasadas por pares; '
          'los tiempos de choque son aproximados. Reduce el paso y compara observables, no solo trayectorias. '
          'La presión es impulso acumulado / (6L²t); 2K/(3V) es una referencia diluida, sin corrección de volumen excluido. '
          'El recipiente intercambia momento con el gas; la energía cinética se conserva. '
          'La distribución de rapidez es una realización finita, sin intervalo estadístico. Los marcadores representan centros; su tamaño es ilustrativo.')
    return packet(config,t,np.column_stack([energy,collisions,pressures]),data,visual,
        [chart('Energía cinética','Tiempo (s)','K (J)',line(t,energy)),
         chart('Presión acumulada en paredes','Tiempo (s)','Pa',line(t[1:],pressures[1:],'Paredes'),line(t,np.full(len(t),ideal),'Referencia diluida',linestyle='--')),
         chart('Rapideces finales','Rapidez (m/s)','Partículas',line(speeds,np.zeros(n),kind='hist')),
         chart('Choques entre partículas','Tiempo (s)','Conteo acumulado',line(t,collisions))],
        [metric(n,'Esferas simuladas','.0f'),metric(count,'Choques por pares','.0f'),metric(drift,'Deriva relativa de energía','.2e'),metric(pressures[-1],'Presión media en paredes · Pa')],
        note,positions=positions,velocities=velocities,energy=energy,momentum_balance=balance,
        datasets={'Trayectorias de partículas':particle_frames(t,positions,velocities,'m')})


def pair_acceleration(positions, mass, charges, coupling, softening, interaction):
    """Suma por pares de fuerzas centrales con potencial de Plummer."""
    n=len(positions);ii,jj=np.triu_indices(n,1)
    displacement=positions[ii]-positions[jj]
    distance2=np.sum(displacement**2,axis=1)+softening**2
    coefficient = (-coupling*mass*mass*np.ones(len(ii)) if interaction=='gravity'
                   else coupling*charges[ii]*charges[jj])
    force=coefficient[:,None]*displacement/distance2[:,None]**1.5
    acceleration=np.zeros_like(positions)
    np.add.at(acceleration,ii,force/mass);np.add.at(acceleration,jj,-force/mass)
    potential=np.sum(coefficient/np.sqrt(distance2))
    return acceleration,float(potential)


def initial_cloud(p, seed):
    rng=np.random.default_rng(seed);n=p['bodies']
    pos=rng.normal(size=(n,3));pos*=p['cloud_radius']/np.max(np.linalg.norm(pos,axis=1))
    if p['geometry']=='disk':pos[:,2]*=.12
    pos-=pos.mean(axis=0)
    vel=rng.normal(size=(n,3))*p['dispersion']/np.sqrt(3)
    tangent=np.column_stack([-pos[:,1],pos[:,0],np.zeros(n)])
    tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-15)
    vel+=p['rotation']*tangent;vel-=vel.mean(axis=0)
    charges=np.where(np.arange(n)%2==0,p['charge'],-p['charge'])
    return pos,vel,charges


def integrate_cloud(p, config, divisor=1):
    pos,vel,charges=initial_cloud(p,config.seed)
    t=np.linspace(0,config.duration,config.solver.points)
    positions=np.empty((len(t),len(pos),3));velocities=np.empty_like(positions);potential=np.empty(len(t))
    acceleration,potential[0]=pair_acceleration(pos,p['body_mass'],charges,p['coupling'],p['softening'],p['interaction'])
    positions[0],velocities[0]=pos,vel;steps=0
    for frame in range(1,len(t)):
        span=t[frame]-t[frame-1];substeps=max(1,int(np.ceil(span/p['step'])))*divisor;dt=span/substeps
        for _ in range(substeps):
            pos=pos+dt*vel+.5*dt*dt*acceleration
            following,U=pair_acceleration(pos,p['body_mass'],charges,p['coupling'],p['softening'],p['interaction'])
            vel=vel+.5*dt*(acceleration+following);acceleration=following;steps+=1
        positions[frame],velocities[frame],potential[frame]=pos,vel,U
    if not np.isfinite(positions).all() or not np.isfinite(velocities).all():
        raise ValueError('La nube produjo valores no finitos; reduce el paso o el acoplamiento.')
    return t,positions,velocities,potential,charges,steps


def nbody(config,p):
    t,positions,velocities,U,charges,steps=integrate_cloud(p,config)
    _,ref,_,_,_,_=integrate_cloud(p,config,2)
    K=.5*p['body_mass']*np.sum(velocities**2,axis=(1,2));energy=K+U
    scale=max(K[0]+abs(U[0]),1e-30);drift=np.max(np.abs(energy-energy[0]))/scale
    momentum=p['body_mass']*np.sum(velocities,axis=1)
    angular=p['body_mass']*np.sum(np.cross(positions,velocities),axis=1)
    error=np.max(np.linalg.norm(positions-ref,axis=2))
    rms=np.sqrt(np.mean(np.sum(positions**2,axis=2),axis=1))
    data=pd.DataFrame(dict(t_uT=t,K_uE=K,U_uE=U,E_uE=energy,rms_radius_uL=rms))
    for j,axis in enumerate('xyz'):
        data['P'+axis+'_uM_uL_uT']=momentum[:,j];data['L'+axis+'_uM_uL2_uT']=angular[:,j]
    visual=scene(positions[:,0],['x (uL)','y (uL)','z (uL)'],'N CUERPOS · FUERZAS MUTUAS',particles=positions,
                 particle_colors=charges if p['interaction']=='electric' else np.arange(p['bodies']),charge_colors=p['interaction']=='electric',physical=True,trail_count=8)
    note=(f'<b>Velocity Verlet · potencial suavizado · float64</b><br>Semilla = {config.seed}; {steps} subpasos; '
          f'Δt ≤ {p["step"]:g} uT. Deriva de energía / (K₀+|U₀|): {drift:.5g}. '
          f'Diferencia máxima de posición con Δt/2: {error:.5g} uL.<br>'
          'Son unidades reducidas: uE = uM·uL²/uT²; el acoplamiento y las cargas se expresan en estas unidades. '
          'ε es parte del potencial físico elegido, no una tolerancia del integrador. '
          'No hay paredes, fusiones, impactos, radiación ni efectos relativistas. '
          'La interacción eléctrica representa cargas clásicas suavizadas, no una simulación cuántica ni un plasma experimental calibrado. '
          'La comparación de pasos es empírica; en dinámicas sensibles puede crecer con el tiempo. '
          'Azul/ámbar distinguen signos en el caso eléctrico. Los marcadores indican centros; las colas muestran hasta ocho partículas.')
    return packet(config,t,positions[:,0],data,visual,
        [chart('Balance energético','Tiempo (uT)','uE',line(t,K,'Cinética'),line(t,U,'Potencial'),line(t,energy,'Total')),
         chart('Deriva normalizada de energía','Tiempo (uT)','(E−E₀)/(K₀+|U₀|)',line(t,(energy-energy[0])/scale)),
         chart('Radio RMS de la nube','Tiempo (uT)','uL',line(t,rms)),
         chart('Conservación de momento','Tiempo (uT)','|P−P₀|',line(t,np.linalg.norm(momentum-momentum[0],axis=1)))],
        [metric(p['bodies'],'Partículas interactuantes','.0f'),metric(drift,'Deriva energética normalizada','.2e'),
         metric(np.max(np.linalg.norm(momentum-momentum[0],axis=1)),'Cambio máximo de momento','.2e'),metric(error,'Diferencia al reducir paso · uL','.2e')],
        note,positions=positions,velocities=velocities,energy=energy,momentum=momentum,angular=angular,
        refinement_positions=ref,charges=charges,datasets={'Trayectorias de partículas':particle_frames(t,positions,velocities,'uL'),
           'Propiedades iniciales':pd.DataFrame(dict(particle=np.arange(1,p['bodies']+1),mass_uM=p['body_mass'],charge_uQ=charges))})


def run_particles(config,p):
    return {'gas_box':gas_box,'nbody':nbody}[config.model](config,p)
