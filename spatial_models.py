"""Escenarios 3D de interacción fotón-electrón, confinamiento y geometría."""
import numpy as np
import pandas as pd
from scipy.constants import c, m_e, physical_constants
from scipy.integrate import trapezoid, cumulative_trapezoid
from advanced_models import scene, chart, line, metric, packet, numeric, numeric_note
from particle_data import MEV_J

SPATIAL_MODELS={'compton','paul_trap','surface','geodesic'}


def validate_spatial(model,p,config):
    if model=='surface' and p['shape']=='torus' and p['minor']>=p['radius']:
        raise ValueError('El toro regular requiere radio menor r < radio mayor R.')
    if model=='surface' and p['shape']=='mobius' and p['minor']>.6*p['radius']:
        raise ValueError('Usa semianchura ≤ 0.6R para la banda de Möbius mostrada.')
    if model=='paul_trap' and config.duration*p['rf']>1000:
        raise ValueError('Reduce frecuencia o duración: ΩT ≤ 1000 en esta exploración.')


def compton_kinematics(energy,theta,phi=0.):
    rest=m_e*c*c/MEV_J
    ratio=1/(1+(energy/rest)*(1-np.cos(theta)))
    outgoing=energy*ratio
    direction=np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
    recoil=np.array([0.,0.,energy])-outgoing*direction
    kinetic=energy-outgoing
    return outgoing,kinetic,recoil,direction


def compton(config,p):
    theta,phi=np.deg2rad([p['theta'],p['phi']]);E=p['photon_energy'];rest=m_e*c*c/MEV_J
    outgoing,K,recoil,direction=compton_kinematics(E,theta,phi)
    t=np.linspace(-config.duration/2,config.duration/2,config.solver.points)*1e-9
    photon=np.where((t<0)[:,None],c*t[:,None]*np.array([0.,0.,1.]),c*t[:,None]*direction)
    electron=np.maximum(t,0)[:,None]*c*recoil/(rest+K)
    angle=np.linspace(0,np.pi,361);ratio=1/(1+E/rest*(1-np.cos(angle)))
    re=physical_constants['classical electron radius'][0]
    cross=.5*re**2*ratio**2*(ratio+1/ratio-np.sin(angle)**2)/1e-28
    scan=pd.DataFrame(dict(theta_deg=np.rad2deg(angle),photon_MeV=E*ratio,electron_kinetic_MeV=E*(1-ratio),dsigma_barn_sr=cross))
    residual=abs((rest+K)**2-np.dot(recoil,recoil)-rest**2)/rest**2
    data=pd.DataFrame(dict(t_s=t,photon_x_m=photon[:,0],photon_y_m=photon[:,1],photon_z_m=photon[:,2],
                           electron_x_m=electron[:,0],electron_y_m=electron[:,1],electron_z_m=electron[:,2]))
    visual=scene(photon,['x (m)','y (m)','z (m)'],'COMPTON · FOTÓN Y ELECTRÓN',physical=True,
                 tracks=[dict(xyz=electron,label='Electrón de retroceso',animate=True)],origins=[[0,0,0]])
    return packet(config,t,np.column_stack([photon,electron]),data,visual,
        [chart('Energía del fotón dispersado','θ (°)','MeV',line(scan.theta_deg,scan.photon_MeV)),
         chart('Energía cinética de retroceso','θ (°)','MeV',line(scan.theta_deg,scan.electron_kinetic_MeV)),
         chart('Klein–Nishina · fotón no polarizado','θ (°)','dσ/dΩ (barn/sr)',line(scan.theta_deg,cross)),
         chart('Proyección del evento','z (m)','x (m)',line(photon[:,2],photon[:,0],'Fotón'),line(electron[:,2],electron[:,0],'Electrón'))],
        [metric(outgoing,'Energía del fotón final · MeV'),metric(K,'Energía cinética del electrón · MeV'),
         metric(np.linalg.norm(recoil)/(rest+K),'Rapidez de retroceso / c'),metric(residual,'Residuo de masa normalizado','.2e')],
        '<b>Cinemática Compton analítica · float64</b><br>Electrón libre inicialmente en reposo, evento en t=0. '
        'Antes del evento el fotón va hacia +Z; después salen el fotón y el electrón. '
        'Se conservan energía y momento. El residuo comprueba la relación relativista del electrón, no es una cota de error. '
        'Klein–Nishina corresponde a fotones no polarizados y es una sección eficaz diferencial, no una probabilidad angular normalizada. '
        'No se modelan electrones ligados, múltiples dispersiones ni creación de pares. El ángulo se elige, no se muestrea.',
        electron_momentum=recoil,photon_energy=outgoing,electron_kinetic=K,
        datasets={'Barrido angular Compton':scan,'Cuatro-momentos':pd.DataFrame([
            [E,0,0,E],[rest,0,0,0],[outgoing,*(outgoing*direction)],[rest+K,*recoil]],
            columns=['E_MeV','px_MeV_c','py_MeV_c','pz_MeV_c'],index=['Fotón inicial','Electrón inicial','Fotón final','Electrón final']).reset_index(names='objeto')})


def paul_trap(config,p):
    a=p['a']*np.array([1.,1.,-2.]);q=p['q']*np.array([1.,1.,-2.]);rf=p['rf']
    def rhs(t,y):return np.r_[y[3:],-.25*rf**2*(a-2*q*np.cos(rf*t))*y[:3]]
    initial=[p['x0'],p['y0'],p['z0'],p['vx0'],p['vy0'],p['vz0']]
    t,y,ref,diff=numeric(rhs,initial,config.duration,config.solver)
    if np.max(np.abs(y))>1e8:raise ValueError('La trayectoria sale del dominio de visualización |estado| ≤ 10⁸; reduce a, q o duración.')
    K=.5*np.sum(y[:,3:]**2,axis=1)
    U=rf**2/8*np.sum((a[None,:]-2*q[None,:]*np.cos(rf*t[:,None]))*y[:,:3]**2,axis=1)
    power=rf**3/4*np.sin(rf*t)*np.sum(q[None,:]*y[:,:3]**2,axis=1)
    work=cumulative_trapezoid(power,t,initial=0);residual=K+U-K[0]-U[0]-work
    data=pd.DataFrame(y,columns=['x_uL','y_uL','z_uL','vx_uL_uT','vy_uL_uT','vz_uL_uT'])
    data.insert(0,'t_uT',t);data['K_per_mass']=K;data['U_per_mass']=U;data['work_residual']=residual
    return packet(config,t,y,data,scene(y[:,:3],['x (uL)','y (uL)','z (uL)'],'PAUL · CONFINAMIENTO CUADRUPOLAR',physical=True,origins=[[0,0,0]]),
        [chart('Movimiento en tres ejes','Tiempo (uT)','uL',*[line(t,y[:,i],s) for i,s in enumerate('xyz')]),
         chart('Plano de fases radial','x (uL)','vx (uL/uT)',line(y[:,0],y[:,3])),
         chart('Energía específica variable','Tiempo (uT)','uL²/uT²',line(t,K,'Cinética'),line(t,U,'Potencial'),line(t,K+U,'Total')),
         chart('Balance con trabajo RF · muestreado','Tiempo (uT)','E−E₀−∫∂U/∂t dt',line(t,residual))],
        [metric(np.max(np.linalg.norm(y[:,:3],axis=1)),'Radio máximo muestreado · uL'),metric(2*np.pi/rf,'Período RF · uT'),
         metric(np.max(abs(residual)),'Residuo de trabajo muestreado'),metric(diff,'Diferencia refinada normalizada','.2e')],
        numeric_note(config,diff,'Modelo de Mathieu ideal, sin colisiones ni carga espacial; a y q incorporan masa, carga y voltajes en unidades reducidas. '
                     'Las sumas de los coeficientes cuadrupolares son cero (Laplace). La fuente RF realiza trabajo: la energía mecánica no se conserva. '
                     'El balance usa cuadratura trapezoidal de los puntos de salida y puede requerir más muestreo que la trayectoria. '
                     'Permanecer acotado un tiempo finito no demuestra estabilidad asintótica; no se representa la geometría de electrodos.'),refined=ref)


def surface_mesh(shape,R,r,curvature,n):
    if shape=='sphere':
        u,v=np.meshgrid(np.linspace(0,2*np.pi,n),np.linspace(0,np.pi,n));xyz=np.stack([R*np.sin(v)*np.cos(u),R*np.sin(v)*np.sin(u),R*np.cos(v)],axis=2)
    elif shape=='torus':
        u,v=np.meshgrid(np.linspace(0,2*np.pi,n),np.linspace(0,2*np.pi,n));xyz=np.stack([(R+r*np.cos(v))*np.cos(u),(R+r*np.cos(v))*np.sin(u),r*np.sin(v)],axis=2)
    elif shape=='mobius':
        u,v=np.meshgrid(np.linspace(0,2*np.pi,n),np.linspace(-r,r,n));xyz=np.stack([(R+v*np.cos(u/2))*np.cos(u),(R+v*np.cos(u/2))*np.sin(u),v*np.sin(u/2)],axis=2)
    else:
        u,v=np.meshgrid(np.linspace(-R,R,n),np.linspace(-R,R,n));xyz=np.stack([u,v,curvature*(u*u-v*v)],axis=2)
    return xyz,u,v


def mesh_area(xyz):
    a=xyz[:-1,:-1];b=xyz[1:,:-1];cc=xyz[:-1,1:];d=xyz[1:,1:]
    return .5*(np.linalg.norm(np.cross(b-a,cc-a),axis=2).sum()+np.linalg.norm(np.cross(d-b,cc-b),axis=2).sum())


def surface(config,p):
    mesh,u,v=surface_mesh(p['shape'],p['radius'],p['minor'],p['curvature'],p['resolution'])
    finer,*_=surface_mesh(p['shape'],p['radius'],p['minor'],p['curvature'],2*p['resolution']-1)
    area=mesh_area(mesh);reference=mesh_area(finer)
    exact={'sphere':4*np.pi*p['radius']**2,'torus':4*np.pi**2*p['radius']*p['minor']}.get(p['shape'])
    path=mesh[mesh.shape[0]//2];parameter=np.arange(len(path),dtype=float)
    points=mesh.reshape(-1,3);data=pd.DataFrame(points,columns=['x_uL','y_uL','z_uL']);data.insert(0,'v',v.ravel());data.insert(0,'u',u.ravel())
    widths=np.ptp(points,axis=0)
    return packet(config,parameter,path,data,scene(path,['x (uL)','y (uL)','z (uL)'],'GEOMETRÍA · SUPERFICIE PARAMÉTRICA',physical=True,mesh=mesh),
        [chart('Curva paramétrica seleccionada','Índice de muestra','uL',*[line(parameter,path[:,i],s) for i,s in enumerate('xyz')]),
         chart('Sección de la malla','x (uL)','z (uL)',line(path[:,0],path[:,2])),
         chart('Área por triangulación','Resolución por eje','uL²',line([p['resolution'],2*p['resolution']-1],[area,reference],kind='scatter')),
         chart('Extensión de la geometría','Eje 0=x, 1=y, 2=z','uL',line(np.arange(3),widths,kind='bar'))],
        [metric(area,'Área de malla · uL²'),metric(abs(area-reference),'Diferencia al refinar malla · uL²'),
         metric(exact,'Área analítica · uL²') if exact is not None else ('n/a','Área analítica no usada'),metric(len(points),'Vértices paramétricos','.0f')],
        '<b>Malla paramétrica · float64</b><br>Área = suma de áreas de triángulos; comparación con malla de doble resolución menos uno. '
        'La diferencia de mallas no es una cota garantizada. Esfera/toro incluyen una referencia analítica. '
        'La banda de Möbius es no orientable y sus extremos se identifican con inversión de v. Los vértices de la costura se repiten en el CSV. '
        'La animación recorre una fila paramétrica, no es una simulación de movimiento físico. En Möbius la fila central representa el círculo central solo con resolución impar. '
        'R escala la esfera, el radio mayor del toro/banda o el semidominio del paraboloide. r solo afecta al toro y a la banda.',
        mesh=mesh,area=area,area_reference=reference,area_exact=exact)


def geodesic(config,p):
    lat,lon,bearing=np.deg2rad([p['latitude'],p['longitude'],p['bearing']]);R=p['radius']
    start=np.array([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])
    north=np.array([-np.sin(lat)*np.cos(lon),-np.sin(lat)*np.sin(lon),np.cos(lat)])
    east=np.array([-np.sin(lon),np.cos(lon),0.]);tangent=np.cos(bearing)*north+np.sin(bearing)*east
    t=np.linspace(0,config.duration,config.solver.points);phase=p['angular_speed']*t
    xyz=R*(np.cos(phase)[:,None]*start+np.sin(phase)[:,None]*tangent)
    arc=R*phase;chord=np.linalg.norm(xyz-xyz[0],axis=1);radius=np.linalg.norm(xyz,axis=1)
    mesh,*_=surface_mesh('sphere',R,.2,0.,40)
    data=pd.DataFrame(dict(t_uT=t,x_uL=xyz[:,0],y_uL=xyz[:,1],z_uL=xyz[:,2],arc_uL=arc,chord_uL=chord,
                           latitude_deg=np.rad2deg(np.arcsin(np.clip(xyz[:,2]/R,-1,1))),longitude_deg=np.rad2deg(np.arctan2(xyz[:,1],xyz[:,0]))))
    return packet(config,t,xyz,data,scene(xyz,['x (uL)','y (uL)','z (uL)'],'GEODÉSICA · CÍRCULO MÁXIMO',physical=True,mesh=mesh),
        [chart('Arco recorrido y cuerda','Tiempo (uT)','uL',line(t,arc,'Arco'),line(t,chord,'Cuerda')),
         chart('Latitud','Tiempo (uT)','°',line(t,data.latitude_deg)),chart('Longitud · salto en ±180°','Tiempo (uT)','°',line(t,data.longitude_deg)),
         chart('Restricción esférica','Tiempo (uT)','|r|−R (uL)',line(t,radius-R))],
        [metric(arc[-1],'Longitud de arco recorrida · uL'),metric(chord[-1],'Cuerda final · uL'),metric(1/R,'Curvatura extrínseca · 1/uL'),metric(np.max(abs(radius-R)),'Residuo radial máximo · uL','.2e')],
        '<b>Geodésica esférica analítica</b><br>La dirección inicial se fija por rumbo desde el norte hacia el este. '
        'La curva es un círculo máximo y su aceleración es normal a la esfera. Solo los arcos de ángulo ≤ π son mínimos entre extremos; '
        'el arco acumulado puede dar varias vueltas. Latitud/longitud tienen singularidades de coordenadas en polos y costura, sin salto espacial. '
        'El residuo radial mide redondeo de la fórmula, no incertidumbre física.',mesh=mesh)


def run_spatial(config,p):
    return {'compton':compton,'paul_trap':paul_trap,'surface':surface,'geodesic':geodesic}[config.model](config,p)
