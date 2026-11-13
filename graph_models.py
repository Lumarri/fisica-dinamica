"""Grafos 3D y dinámica sobre su Laplaciano, sin dependencias de servicios."""
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components,dijkstra
from advanced_models import packet,scene,chart,line,metric,numeric,numeric_note

GRAPH_MODELS={'graph_routes','graph_heat','graph_waves'}


def validate_graph(model,p,config):
    if p['source']>p['nodes'] or p['target']>p['nodes']:
        raise ValueError('Origen/destino deben estar entre 1 y N; destino 0 significa último nodo.')
    if p['topology']=='small_world' and 2*p['neighbors']>=p['nodes']:
        raise ValueError('La red de mundo pequeño requiere 2·vecinos por lado < N.')


def make_graph(p,seed):
    rng=np.random.default_rng(seed);n=p['nodes'];A=np.zeros((n,n));pos=rng.uniform(-1,1,(n,3))
    if p['topology']=='grid':
        side=int(np.ceil(n**(1/3)));pos=np.array([(i//(side*side),(i//side)%side,i%side) for i in range(n)],float)
        A=(np.abs(pos[:,None]-pos[None,:]).sum(axis=2)==1).astype(float)
        pos-=pos.mean(axis=0);pos/=max(side-1,1)
    elif p['topology']=='small_world':
        angle=2*np.pi*np.arange(n)/n;pos=np.column_stack([np.cos(angle),np.sin(angle),.25*np.sin(3*angle)])
        for i in range(n):
            for offset in range(1,p['neighbors']+1):A[i,(i+offset)%n]=A[(i+offset)%n,i]=1
        for i in range(n):
            for offset in range(1,p['neighbors']+1):
                j=(i+offset)%n
                if rng.random()<p['probability']:
                    options=np.flatnonzero((A[i]==0)&(np.arange(n)!=i))
                    if len(options):
                        k=rng.choice(options);A[i,j]=A[j,i]=0;A[i,k]=A[k,i]=1
    elif p['topology']=='geometric':
        A=(np.linalg.norm(pos[:,None]-pos[None,:],axis=2)<p['link_radius']).astype(float);np.fill_diagonal(A,0)
    else:
        upper=np.triu(rng.random((n,n))<p['probability'],1);A=(upper|upper.T).astype(float)
    ii,jj=np.nonzero(np.triu(A,1));edges=np.column_stack([ii,jj]).astype(int)
    distance=np.linalg.norm(pos[:,None]-pos[None,:],axis=2)
    costs=A.copy() if p['weights']=='unit' else A*distance
    weights=A.copy() if p['weights']=='unit' else np.divide(A,distance,out=np.zeros_like(A),where=distance>0)
    L=np.diag(weights.sum(axis=1))-weights
    components,labels=connected_components(csr_matrix(A),directed=False)
    return dict(A=A,pos=pos,edges=edges,costs=costs,W=weights,L=L,components=components,labels=labels,distance=distance)


def graph_datasets(g):
    edges=g['edges'];i,j=edges.T if len(edges) else (np.array([],int),np.array([],int))
    return {'Aristas y pesos':pd.DataFrame(dict(node_i=i+1,node_j=j+1,length_uL=g['distance'][i,j],route_cost=g['costs'][i,j],coupling_weight=g['W'][i,j])),
            'Matriz de adyacencia':pd.DataFrame(g['A'],columns=[f'nodo_{i+1}' for i in range(len(g['A']))]).rename_axis('nodo_desde_0').reset_index()}


def graph_scene(g,t,values,title,positions=None,**kwargs):
    if positions is None:positions=np.broadcast_to(g['pos'],(len(t),*g['pos'].shape)).copy()
    return scene(positions[:,0],['x (uL)','y (uL)','z (uL)'],title,particles=positions,
                 particle_colors=values[0],node_values=values,edges=g['edges'],trail_count=0,physical=True,**kwargs)


def graph_routes(config,p):
    g=make_graph(p,config.seed);n=p['nodes'];source=p['source']-1;target=(p['target'] or n)-1
    distances,previous=dijkstra(csr_matrix(g['costs']),directed=False,indices=source,return_predecessors=True)
    route=[]
    if np.isfinite(distances[target]):
        current=target
        while current!=source:route.append(current);current=int(previous[current])
        route.append(source);route=route[::-1]
    degree=g['A'].sum(axis=1);triangles=np.diag(g['A']@g['A']@g['A'])
    clustering=np.divide(triangles,degree*(degree-1),out=np.zeros(n),where=degree>1)
    eigen=np.linalg.eigvalsh(g['L']);t=np.arange(max(len(route),2),dtype=float)
    values=np.broadcast_to(degree,(len(t),n)).copy()
    data=pd.DataFrame(dict(node=np.arange(1,n+1),x_uL=g['pos'][:,0],y_uL=g['pos'][:,1],z_uL=g['pos'][:,2],
                           degree=degree,component=g['labels']+1,clustering=clustering,reachable=np.isfinite(distances).astype(int)))
    # Distancias no alcanzables se exportan separadas como NA, sin inventar un coste.
    route_data=pd.DataFrame(dict(step=np.arange(len(route)),node=np.asarray(route)+1,cumulative_cost=distances[route]))
    aux=graph_datasets(g);aux['Ruta mínima']=route_data
    aux['Distancias desde origen']=pd.DataFrame(dict(node=np.arange(1,n+1),cost=np.where(np.isfinite(distances),distances,np.nan),reachable=np.isfinite(distances)))
    unique,counts=np.unique(degree,return_counts=True)
    return packet(config,t,np.broadcast_to(g['pos'][source],(len(t),3)).copy(),data,
        graph_scene(g,t,values,'GRAFO 3D · CONECTIVIDAD Y RUTAS',focus_path=route,highlight_edges=np.array(list(zip(route[:-1],route[1:])),int).reshape(-1,2),color_label='Grado del nodo'),
        [chart('Distribución de grados','Grado','Nodos',line(unique,counts,kind='bar')),
         chart('Grado por nodo','Nodo (desde 1)','Grado',line(np.arange(1,n+1),degree)),
         chart('Espectro del Laplaciano ponderado','Índice','λ',line(np.arange(n),eigen,kind='scatter')),
         chart('Ruta mínima elegida','Paso','Coste acumulado',line(np.arange(len(route)),distances[route]))],
        [metric(len(g['edges']),'Aristas no dirigidas','.0f'),metric(g['components'],'Componentes conexas','.0f'),
         metric(distances[target],'Coste de ruta mínima') if route else ('sin ruta','Destino desconectado'),metric(clustering.mean(),'Agrupamiento local medio')],
        '<b>Grafo simple no dirigido · Dijkstra</b><br>Semilla reproducible. El grado cuenta vecinos y el agrupamiento local no es ponderado. '
        'Se admiten redes desconectadas: no se inventan conexiones ni distancias. Destino 0 selecciona el último nodo. '
        'La ruta amarilla minimiza suma de costes positivos; el cursor recorre sus nodos. '
        'En modo longitud, c=ℓ/uL y el peso de acoplamiento es 1/c (ambos reducidos); con pesos unitarios ambos son uno. '
        'Las coordenadas sirven como incrustación 3D; los cruces de aristas no crean nodos. CSV usa identificadores desde 1 salvo la matriz, que declara índice desde 0.',
        graph=g,route=route,datasets=aux)


def graph_heat(config,p):
    g=make_graph(p,config.seed);n=p['nodes'];L=g['L'];eigen,V=np.linalg.eigh(L);eigen=np.maximum(eigen,0)
    t=np.linspace(0,config.duration,config.solver.points);initial=np.zeros(n);initial[p['source']-1]=p['heat']
    y=(np.exp(-p['diffusivity']*t[:,None]*eigen)*(V.T@initial)[None,:])@V.T
    total=y.sum(axis=1);variance=y.var(axis=1);data=pd.DataFrame(y,columns=[f'T_{i+1}_uH' for i in range(n)])
    data.insert(0,'t_uT',t);data['total_uH']=total;data['variance']=variance
    component_mean=np.array([initial[g['labels']==label].mean() for label in g['labels']])
    aux=graph_datasets(g);aux['Equilibrio por componente']=pd.DataFrame(dict(node=np.arange(1,n+1),component=g['labels']+1,limit_uH=component_mean))
    return packet(config,t,y,data,graph_scene(g,t,y,'DIFUSIÓN · LAPLACIANO DEL GRAFO',color_label='Cantidad difundida (uH)'),
        [chart('Hasta seis nodos','Tiempo (uT)','uH',*[line(t,y[:,i],str(i+1)) for i in range(min(6,n))]),
         chart('Cantidad total conservada','Tiempo (uT)','uH',line(t,total)),chart('Varianza entre nodos','Tiempo (uT)','uH²',line(t,variance)),
         chart('Espectro de difusión','Índice','λ',line(np.arange(n),eigen,kind='scatter'))],
        [metric(np.max(abs(total-total[0])),'Deriva de cantidad total · uH','.2e'),metric(variance[-1],'Varianza final'),
         metric(g['components'],'Componentes independientes','.0f'),metric(np.max(abs(y[-1]-component_mean)),'Distancia al equilibrio final · uH')],
        '<b>Difusión continua · descomposición espectral simétrica</b><br>Solución exp(−DLt)T₀ en float64. '
        'Cada nodo tiene capacidad unitaria; uH es cantidad abstracta, no temperatura SI calibrada. '
        'Cada componente conserva su cantidad y converge a su propia media. Un grafo desconectado no tiene un único equilibrio global. '
        'Se redondean a cero autovalores negativos de redondeo; no se recortan las cantidades. '
        'Los colores usan una escala fija para toda la reproducción. Los puntos de salida no controlan una tolerancia de integración.',
        graph=g,equilibrium=component_mean,datasets=aux)


def graph_waves(config,p):
    g=make_graph(p,config.seed);n=p['nodes'];L=g['L']
    def rhs(t,y):return np.r_[y[n:],-(p['anchor']*y[:n]+p['coupling']*(L@y[:n])+p['damping']*y[n:])/p['node_mass']]
    initial=np.zeros(2*n);initial[p['source']-1]=p['displacement']
    t,y,ref,diff=numeric(rhs,initial,config.duration,config.solver);x,v=y[:,:n],y[:,n:]
    K=.5*p['node_mass']*np.sum(v*v,axis=1)
    U=.5*p['anchor']*np.sum(x*x,axis=1)+.5*p['coupling']*np.sum(x*(x@L),axis=1);energy=K+U
    positions=np.broadcast_to(g['pos'],(len(t),n,3)).copy();positions[:,:,2]+=x
    frequency=np.sqrt((p['anchor']+p['coupling']*np.maximum(np.linalg.eigvalsh(L),0))/p['node_mass'])
    data=pd.DataFrame(x,columns=[f'x_{i+1}_uL' for i in range(n)])
    for i in range(n):data[f'v_{i+1}_uL_uT']=v[:,i]
    data.insert(0,'t_uT',t);data['E_uE']=energy
    aux=graph_datasets(g);aux['Modos normales']=pd.DataFrame(dict(mode=np.arange(1,n+1),omega_rad_uT=frequency))
    return packet(config,t,y,data,graph_scene(g,t,x,'RED DE OSCILADORES · MODOS ACOPLADOS',positions=positions,color_label='Desplazamiento escalar (uL)'),
        [chart('Desplazamientos · seis nodos','Tiempo (uT)','uL',*[line(t,x[:,i],str(i+1)) for i in range(min(6,n))]),
         chart('Energía de la red','Tiempo (uT)','uE',line(t,K,'Cinética'),line(t,U,'Potencial'),line(t,energy,'Total')),
         chart('Frecuencias normales sin amortiguamiento','Modo','rad/uT',line(np.arange(1,n+1),frequency,kind='scatter')),
         chart('Velocidad del nodo excitado','Tiempo (uT)','uL/uT',line(t,v[:,p['source']-1]))],
        [metric(energy[0],'Energía inicial · uE'),metric(energy[-1],'Energía final · uE'),metric(frequency.max(),'Frecuencia modal máxima · rad/uT'),metric(diff,'Diferencia refinada normalizada','.2e')],
        numeric_note(config,diff,'Cada nodo tiene un desplazamiento escalar; las posiciones de la red son una representación. '
                     'Las líneas no son resortes centrales con longitud natural geométrica: el potencial usa diferencias de desplazamiento en el grafo. '
                     'uE = uM·uL²/uT². Sin amortiguamiento se conserva energía; con b≥0, dE/dt=−bΣv². '
                     'Los modos se calculan sin amortiguamiento. La escena mueve cada nodo en Z y mantiene la conectividad.'),
        refined=ref,graph=g,energy=energy,frequencies=frequency,datasets=aux)


def run_graph(config,p):return {'graph_routes':graph_routes,'graph_heat':graph_heat,'graph_waves':graph_waves}[config.model](config,p)
