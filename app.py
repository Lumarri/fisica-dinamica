import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from models import oscillator, lorenz, monte_carlo

st.set_page_config(page_title="Física · Laboratorio dinámico", page_icon="🌀", layout="wide")
st.title("Laboratorio de física y sistemas dinámicos")
st.caption("Explora modelos, formula hipótesis y cuantifica incertidumbre con experimentos reproducibles.")
mode = st.sidebar.selectbox("Experimento", ["Oscilador", "Lorenz", "Monte Carlo"])
duration = st.sidebar.slider("Duración (s; Lorenz usa tiempo adimensional)", 1, 60, 20)
notes = st.sidebar.text_area("Hipótesis y notas de investigación")
parameters = {"model": mode, "duration": duration, "notes": notes}
if mode == "Oscilador":
    st.subheader("Oscilador amortiguado")
    st.latex(r"m\ddot{x}+c\dot{x}+kx=0")
    mass = st.sidebar.number_input("Masa m (kg)", .1, 100., 1.)
    k = st.sidebar.number_input("Rigidez k (N/m)", .1, 100., 4.)
    c = st.sidebar.number_input("Amortiguamiento c (kg/s)", 0., 20., .2)
    x0 = st.sidebar.number_input("Posición inicial (m)", -10., 10., 1.)
    parameters.update(mass=mass, stiffness=k, damping=c, initial=[x0, 0.])
    t, y = oscillator(mass, k, c, (x0, 0.), duration)
    df = pd.DataFrame({"t": t, "x": y[:, 0], "v": y[:, 1]})
    a,b = st.columns(2)
    a.plotly_chart(px.line(df, x="t", y="x", title="Posición (m) / tiempo (s)"), use_container_width=True)
    b.plotly_chart(px.line(df, x="x", y="v", title="Espacio de fases: posición / velocidad"), use_container_width=True)
    energy = .5*mass*y[:, 1]**2+.5*k*y[:, 0]**2
    st.plotly_chart(px.line(x=t, y=energy, labels={"x":"Tiempo (s)", "y":"Energía (J)"}), use_container_width=True)
elif mode == "Lorenz":
    st.subheader("Atractor de Lorenz")
    st.latex(r"\dot{x}=\sigma(y-x),\quad \dot{y}=x(\rho-z)-y,\quad \dot{z}=xy-\beta z")
    rho = st.sidebar.slider("ρ", 0., 60., 28.)
    delta = st.sidebar.number_input("Perturbación inicial Δx", .000001, .1, .0001, format="%.6f")
    parameters.update(sigma=10., rho=rho, beta=8/3, initial=[1.,1.,1.], delta=delta)
    t, y = lorenz(rho=rho, duration=duration)
    _, perturbed = lorenz(rho=rho, initial=(1+delta,1.,1.), duration=duration)
    df = pd.DataFrame({"t":t,"x":y[:,0],"y":y[:,1],"z":y[:,2], "separacion":np.linalg.norm(y-perturbed, axis=1)})
    st.plotly_chart(px.line_3d(df,x="x",y="y",z="z",title="Trayectoria tridimensional"), use_container_width=True)
    st.plotly_chart(px.line(df,x="t",y="separacion",log_y=True,title="Sensibilidad a condiciones iniciales"), use_container_width=True)
    st.caption("Parámetros y variables adimensionales. La separación por sí sola no estima un exponente de Lyapunov.")
else:
    st.subheader("Monte Carlo · incertidumbre en la rigidez")
    st.write("Oscilador sin amortiguamiento: m = 1 kg, x₀ = 1 m, v₀ = 0. La rigidez sigue una distribución uniforme positiva.")
    count = st.sidebar.slider("Número de realizaciones", 100, 5000, 1000, 100)
    seed = st.sidebar.number_input("Semilla", 0, 2147483647, 42)
    mean = st.sidebar.slider("Rigidez media (N/m)", 1., 10., 4.)
    std = st.sidebar.slider("Desviación de rigidez (N/m)", 0., .5, .4)
    threshold = st.sidebar.slider("Umbral de posición final (m)", -1., 1., .5)
    parameters.update(count=count, seed=seed, mean=mean, std=std, threshold=threshold)
    t, paths, terminal, prob, se = monte_carlo(count, seed, mean, std, duration, threshold)
    lo, med, hi = np.quantile(paths,[.025,.5,.975],axis=0)
    fig = go.Figure()
    fig.add_scatter(x=t,y=lo,name="Percentil 2.5",line_color="#9cc9ec")
    fig.add_scatter(x=t,y=hi,name="Percentil 97.5",fill="tonexty",line_color="#9cc9ec")
    fig.add_scatter(x=t,y=med,name="Mediana",line_color="#1768ac")
    fig.update_layout(title="Intervalo central del 95 % de las realizaciones",xaxis_title="Tiempo (s)",yaxis_title="Posición (m)")
    st.plotly_chart(fig,use_container_width=True)
    st.plotly_chart(px.histogram(x=terminal,nbins=40,labels={"x":"Posición final (m)"}),use_container_width=True)
    st.metric("P(posición final > umbral) estimada", f"{prob:.1%}")
    st.caption(f"Error estándar Monte Carlo aproximado: {se:.4f}. La banda representa dispersión del modelo, no un intervalo de confianza de la media.")
    df = pd.DataFrame({"realizacion":np.arange(count),"posicion_final":terminal})
st.download_button("Descargar resultados CSV", df.to_csv(index=False), "resultados.csv", "text/csv")
st.download_button("Descargar configuración y notas", json.dumps(parameters,ensure_ascii=False,indent=2), "experimento.json", "application/json")
st.info("Prototipo de exploración científica. Contrasta los modelos y supuestos con datos antes de extraer conclusiones de investigación.")
