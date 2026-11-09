"""Sistemas dinámicos: trayectorias vecinas y barridos de horizonte finito."""
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from advanced_models import numeric, numeric_note, packet, chart, scene, line, metric

DYNAMIC_MODELS={'rossler','van_der_pol','lotka_volterra','sir','henon','kuramoto'}
SWEEP_PARAMETERS={'rossler':'c','van_der_pol':'mu','lotka_volterra':'growth','sir':'infection','henon':'a','kuramoto':'coupling'}


def validate_dynamics(model,p,config):
    if p['sweep_low']>=p['sweep_high']:
        raise ValueError('El barrido necesita mínimo < máximo.')
    if model=='sir' and (p['s0']+p['i0']>1 or p['perturbation']>=p['s0']):
        raise ValueError('S₀+I₀ debe ser ≤ 1 y la perturbación debe ser menor que S₀.')
    if model=='henon' and p['discard']>=p['iterations']-50:
        raise ValueError('Deja al menos 50 puntos de Hénon tras el transitorio.')
    if model!='henon' and p['sweep_points']*config.duration/config.solver.max_step>250_000:
        raise ValueError('Barrido demasiado costoso: reduce duración o cantidad de parámetros, o aumenta el paso máximo.')


def dynamic_definition(model,p,seed):
    if model=='rossler':
        def rhs(t,y):
            x,v,z=y
            return [-v-z,x+p['a']*v,p['b']+z*(x-p['c'])]
        return rhs,np.array([p['x0'],p['y0'],p['z0']]),['x','y','z']
    if model=='van_der_pol':
        return lambda t,y:[y[1],p['mu']*(1-y[0]**2)*y[1]-y[0]],np.array([p['x0'],p['v0']]),['x','v']
    if model=='lotka_volterra':
        return lambda t,y:[y[0]*(p['growth']-p['predation']*y[1]),y[1]*(p['conversion']*y[0]-p['mortality'])],np.array([p['prey0'],p['predator0']]),['presas','depredadores']
    if model=='sir':
        return lambda t,y:[-p['infection']*y[0]*y[1],p['infection']*y[0]*y[1]-p['recovery']*y[1],p['recovery']*y[1]],np.array([p['s0'],p['i0'],1-p['s0']-p['i0']]),['S','I','R']
    if model=='kuramoto':
        rng=np.random.default_rng(seed)
        omega=rng.normal(p['omega_mean'],p['omega_std'],p['oscillators'])
        initial=rng.uniform(-np.pi,np.pi,p['oscillators'])
        def rhs(t,y):
            z=np.mean(np.exp(1j*y))
            return omega+p['coupling']*np.imag(z*np.exp(-1j*y))
        return rhs,initial,[f'theta_{i+1}_rad' for i in range(len(initial))]
    raise ValueError('Sistema no reconocido.')


def solution(rhs,initial,t,settings):
    sol=solve_ivp(rhs,(0,float(t[-1])),initial,t_eval=t,method='DOP853',rtol=settings.rtol,
                  atol=settings.atol,max_step=settings.max_step)
    if not sol.success or sol.y.shape[1]!=len(t) or not np.isfinite(sol.y).all():
        raise ValueError('El sistema no permanece integrable en este intervalo; reduce parámetros o duración.')
    return sol.y.T


def henon_orbit(p,initial=None):
    n=p['iterations'];y=np.empty((n,2));y[0]=[p['x0'],p['y0']] if initial is None else initial
    for k in range(1,n):
        x,v=y[k-1];y[k]=[1-p['a']*x*x+v,p['b']*x]
        if np.max(np.abs(y[k]))>1e6 or not np.isfinite(y[k]).all():
            raise ValueError('La órbita de Hénon escapa del dominio |estado| ≤ 10⁶. Cambia a, b o el estado inicial.')
    return y


def parameter_sweep(config,p):
    key=SWEEP_PARAMETERS[config.model]
    values=np.linspace(p['sweep_low'],p['sweep_high'],p['sweep_points'])
    rows=[]
    for value in values:
        q={**p,key:float(value)}
        try:
            if config.model=='henon':
                y=henon_orbit(q);tail=y[p['discard']:,0]
            else:
                rhs,initial,_=dynamic_definition(config.model,q,config.seed)
                times=np.linspace(0,config.duration,300)
                y=solution(rhs,initial,times,config.solver)
                start=int(p['tail_fraction']*len(y))
                if config.model=='sir':tail=y[:,1]
                elif config.model=='kuramoto':tail=np.abs(np.mean(np.exp(1j*y[start:]),axis=1))
                else:tail=y[start:,0]
            rows.append((value,float(np.min(tail)),float(np.max(tail)),float(np.mean(tail)),'válido'))
        except (ValueError,FloatingPointError,OverflowError):
            rows.append((value,np.nan,np.nan,np.nan,'escape / integración fallida'))
    return pd.DataFrame(rows,columns=[key,'minimum','maximum','mean','status'])


def field_spec(rhs,y,model):
    if model not in {'van_der_pol','lotka_volterra','sir'}:return None
    low=np.min(y[:,:2],axis=0);high=np.max(y[:,:2],axis=0)
    span=np.maximum(high-low,.1);low-=.1*span;high+=.1*span
    if model in {'lotka_volterra','sir'}:low=np.maximum(low,0)
    xx,yy=np.meshgrid(np.linspace(low[0],high[0],15),np.linspace(low[1],high[1],15))
    vector=np.array([rhs(0,[x,v] if model!='sir' else [x,v,max(0,1-x-v)])[:2] for x,v in zip(xx.ravel(),yy.ravel())])
    if model=='sir':vector[(xx+yy).ravel()>1]=np.nan
    norm=np.maximum(np.linalg.norm(vector,axis=1),1e-30)
    return dict(x=xx,y=yy,u=(vector[:,0]/norm).reshape(xx.shape),v=(vector[:,1]/norm).reshape(xx.shape))


def run_dynamics(config,p):
    model=config.model
    if model=='henon':
        y=henon_orbit(p);t=np.arange(len(y),dtype=float)
        perturbed=henon_orbit(p,[p['x0']+p['perturbation'],p['y0']]);ref=None;diff=0.;labels=['x','y']
        note='<b>Mapa discreto de Hénon · float64</b><br>Iteración directa; no hay integración temporal ni tolerancias DOP853. '
    else:
        rhs,initial,labels=dynamic_definition(model,p,config.seed)
        t,y,ref,diff=numeric(rhs,initial,config.duration,config.solver)
        neighbour=initial.copy();neighbour[0]+=p['perturbation']
        if model=='sir':neighbour[0]-=2*p['perturbation'];neighbour[1]+=p['perturbation']
        perturbed=solution(rhs,neighbour,t,config.solver)
        note=numeric_note(config,diff)
    if model=='kuramoto':
        separation=np.linalg.norm(np.angle(np.exp(1j*(y-perturbed))),axis=1)
    else:separation=np.linalg.norm(y-perturbed,axis=1)
    sweep=parameter_sweep(config,p);key=SWEEP_PARAMETERS[model]
    valid=int((sweep['status']=='válido').sum())
    note+=(f'<br><b>Comparación y barrido</b><br>Perturbación = {p["perturbation"]:g}; '
           f'{valid}/{len(sweep)} valores integrados en el barrido de {key}. '
           'Cada parámetro comienza con el mismo estado y la misma semilla; no se continúa desde la solución anterior. '
           'La separación es una distancia de estados, no un exponente de Lyapunov. '
           'El barrido muestra extremos muestreados de horizonte finito; no demuestra una bifurcación asintótica. '
           'Los puntos fallidos figuran como NaN y con estado en el CSV. ')
    if model=='henon':
        retained=y[p['discard']:];neighbour_visual=perturbed
        coords=np.column_stack([y,t]);other=np.column_stack([neighbour_visual,t])
        note+=f'Se descartan {p["discard"]} iteraciones en fase y barrido. '
    else:
        retained=y[int(p['tail_fraction']*len(t)):]
        coords=y[:,:3] if model in {'rossler','sir'} else np.column_stack([y[:,:2],t])
        other=perturbed[:,:3] if model in {'rossler','sir'} else np.column_stack([perturbed[:,:2],t])
        note+=f'El barrido usa la fracción final desde t/T = {p["tail_fraction"]:g}, salvo SIR (intervalo completo). '
    visual=scene(coords,labels[:3] if model in {'rossler','sir'} else [*labels[:2],'n' if model=='henon' else 't'],
                 model.upper().replace('_',' ')+' · ESPACIO DE ESTADOS',tracks=[dict(xyz=other,label='Condición vecina',animate=True)])
    data=pd.DataFrame(y,columns=labels);data.insert(0,'n' if model=='henon' else 't',t)
    data['separation']=separation
    for j,label in enumerate(labels):data['neighbor_'+label]=perturbed[:,j]
    series=[line(t,y[:,j],label) for j,label in enumerate(labels[:3])]
    phase=chart('Plano de estados','x' if model=='henon' else labels[0],labels[1],
                line(retained[:,0],retained[:,1],kind='scatter' if model=='henon' else 'line'))
    if model!='henon':
        field=field_spec(rhs,y,model)
        if field:phase['vector_field']=field;phase['title']='Fase · direcciones normalizadas'
    sweep_title='Extremos de x · tramo final'
    if model=='sir':sweep_title='Extremos de I · intervalo completo'
    if model=='kuramoto':
        order=np.abs(np.mean(np.exp(1j*y),axis=1));data['order_parameter']=order
        series=[line(t,order,'Orden R')]
        phases=np.exp(1j*y)
        particles=np.stack([phases.real,phases.imag,np.zeros_like(y)],axis=2)
        visual=scene(particles[:,0],['cos θ','sin θ','0'],'KURAMOTO · FASES EN EL CÍRCULO',particles=particles,
                     particle_colors=np.arange(p['oscillators']),physical=True,trail_count=0)
        phase=chart('Fases de hasta 6 osciladores','t','θ mod 2π',*[line(t,np.angle(phases[:,j]),f'{j+1}') for j in range(min(6,y.shape[1]))])
        sweep_title='Orden R · tramo final'
        metrics=[metric(order[-1],'Orden final R ∈ [0,1]'),metric(np.mean(order[len(t)//2:]),'Orden medio · segunda mitad'),metric(separation[-1],'Distancia angular final'),metric(diff,'Diferencia refinada normalizada','.2e')]
        note+='El orden R mide coherencia de fases, no una probabilidad. Frecuencias normales quenched; las fases se integran sin envolver.'
    elif model=='sir':
        residual=np.max(np.abs(y.sum(axis=1)-1));data['population_residual']=y.sum(axis=1)-1
        peak=int(np.argmax(y[:,1]));R0=p['infection']/p['recovery']
        metrics=[metric(R0,'Número reproductivo β/γ'),metric(y[peak,1],'Pico muestreado de I'),metric(t[peak],'Tiempo del pico de I'),metric(residual,'Residuo máximo S+I+R−1','.2e')]
        note+='S, I y R son fracciones; sin nacimientos ni reinfección. El umbral inicial efectivo es (β/γ)S₀; no es una predicción clínica.'
    elif model=='lotka_volterra':
        invariant=p['conversion']*y[:,0]-p['mortality']*np.log(np.maximum(y[:,0],1e-300))+p['predation']*y[:,1]-p['growth']*np.log(np.maximum(y[:,1],1e-300))
        data['first_integral']=invariant
        metrics=[metric(p['mortality']/p['conversion'],'Presas en equilibrio'),metric(p['growth']/p['predation'],'Depredadores en equilibrio'),metric(np.max(np.abs(invariant-invariant[0])),'Deriva de integral primera','.2e'),metric(diff,'Diferencia refinada normalizada','.2e')]
        note+='Las poblaciones son continuas y adimensionales; los coeficientes no incluyen capacidad de carga.'
    else:
        metrics=[metric(np.min(retained[:,0]),'Mínimo de x · tramo final'),metric(np.max(retained[:,0]),'Máximo de x · tramo final'),metric(separation[-1],'Separación final de estados'),metric(diff,'Diferencia refinada','.2e') if model!='henon' else ('float64','Iteración directa del mapa')]
    charts=[chart('Evolución temporal' if model!='henon' else 'Iteraciones','n' if model=='henon' else 't','Estado',*series),phase,
            chart('Condiciones iniciales vecinas','n' if model=='henon' else 't','Distancia de estados',line(t,np.maximum(separation,1e-16)),yscale='log'),
            chart(sweep_title,key,'R' if model=='kuramoto' else 'I' if model=='sir' else labels[0],line(sweep[key],sweep['minimum'],'Mínimo',kind='scatter'),line(sweep[key],sweep['maximum'],'Máximo',kind='scatter'))]
    return packet(config,t,y,data,visual,charts,metrics,note,refined=ref,separation=separation,perturbed=perturbed,
                  sweep=sweep,datasets={'Barrido de parámetros':sweep})
