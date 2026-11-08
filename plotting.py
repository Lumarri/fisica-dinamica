"""Figuras nativas de Matplotlib; no navegador ni servidor HTTP."""
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from catalog import MODELS
from matplotlib import rcParams
rcParams.update({"mathtext.fontset":"cm", "axes.formatter.use_mathtext":True, "axes.unicode_minus":False})

BG = "#18253a"
FG = "#e2ecfb"
MUTED = "#a3b6d1"
CYAN = "#8ccafb"
BLUE = "#879ff1"
GOLD = "#e3b17e"


NEO_CMAP = LinearSegmentedColormap.from_list("Dynamis", ["#91acff", "#82d0ee", "#74dfcc"])

def style_axis(ax, three_d=False):
    ax.set_facecolor(BG)
    ax.tick_params(colors=MUTED, labelsize=9, labelfontfamily="cmr10")
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(FG)
    if three_d:
        ax.zaxis.label.set_color(MUTED)
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.set_facecolor((.10, .16, .25, .5))
            axis.pane.set_edgecolor((.35, .48, .66, .3))
            axis._axinfo['grid']['color'] = (.50, .61, .76, .22)
    else:
        for spine in ax.spines.values():
            spine.set_color("#354f70")
        ax.grid(color="#354f70", alpha=.5, linewidth=.6)


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, width=8, height=5):
        self.figure = Figure(figsize=(width, height), facecolor=BG, layout="constrained")
        super().__init__(self.figure)
        self.setMinimumSize(320, 260)


class SceneCanvas(PlotCanvas):
    def __init__(self):
        super().__init__(9, 6)
        self.figure.set_layout_engine(None)
        self.figure.subplots_adjust(left=.04, right=.94, bottom=.20, top=.93)
        self.ax = None
        self.result = None
        self.marker = None
        self.plane_artists = []
        self.planes_visible = True
        self.link_artist = None
        self.extra_markers = []

    def draw_result(self, result):
        self.figure.clear()
        self.result = result
        self.ax = ax = self.figure.add_subplot(111, projection="3d")
        style_axis(ax, True)
        self.plane_artists = []
        self.link_artist = None
        self.extra_markers = []
        if 'visual' in result.extra:
            self._draw_visual(result.extra['visual'], result.t)
            return
        c, y, t = result.config, result.states, result.t
        if c.model == "lorenz":
            coords = y
            labels = ["x", "y", "z"]
            self.figure.text(.03, .96, "ESPACIO DE ESTADOS · LORENZ", fontsize=10, color=FG)
            # Trayectoria vecina para observar sensibilidad inicial.
            p = result.extra["perturbed"]
            ax.plot(*p.T, color=GOLD, alpha=.35, lw=.6)
        else:
            coords = np.column_stack([y, t])
            labels = ["Posición x (m)", "Velocidad v (m/s)", "Tiempo (s)"]
            self.figure.text(.03, .96, "POSICIÓN · VELOCIDAD · TIEMPO", fontsize=10, color=FG)
            if c.model == "ensemble":
                e = result.extra
                for i in np.linspace(0, c.count-1, min(24, c.count), dtype=int):
                    velocity = -e["initial"][i]*e["omega"][i]*np.sin(e["omega"][i]*t)+c.v0*np.cos(e["omega"][i]*t)
                    ax.plot(e["paths"][i], velocity, t, color=BLUE, alpha=.13, lw=.7)
        points = coords.reshape(-1, 1, 3)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        collection = Line3DCollection(segments, cmap=NEO_CMAP, linewidth=1.7, alpha=.95)
        collection.set_array(t[:-1])
        ax.add_collection3d(collection)
        self.coordinates = coords
        ranges = []
        for j in range(3):
            lo, hi = np.min(coords[:, j]), np.max(coords[:, j])
            # Incluye el conjunto visible para evitar recortes.
            if c.model == "ensemble" and j == 0:
                lo, hi = min(lo, result.extra['paths'].min()), max(hi, result.extra['paths'].max())
            if c.model == "ensemble" and j == 1:
                amplitude = np.max(np.abs(result.extra['initial'])*result.extra['omega'])+abs(c.v0)
                lo, hi = min(lo, -amplitude), max(hi, amplitude)
            margin = max(float(hi-lo)*.08, .1)
            ranges.append((lo-margin, hi+margin))
        ax.set_xlim(*ranges[0]); ax.set_ylim(*ranges[1]); ax.set_zlim(*ranges[2])
        ax.set_xlabel(labels[0], labelpad=5); ax.set_ylabel(labels[1], labelpad=5)
        ax.set_zlabel(labels[2], labelpad=5)
        ax.set_box_aspect((1, 1, .85), zoom=1.03)
        self._draw_planes(ranges)
        self.marker, = ax.plot([coords[0, 0]], [coords[0, 1]], [coords[0, 2]],
                              marker="o", markersize=6, color=GOLD, markeredgecolor=FG)
        self.view("Perspectiva")

    def _draw_visual(self, visual, parameter):
        ax = self.ax
        coords = visual['xyz']
        self.coordinates = coords
        self.figure.text(.03, .96, visual['title'], fontsize=10, color=FG)
        all_coords = [coords]
        for i, track in enumerate(visual.get('tracks', [])):
            points = track['xyz']
            color = [GOLD, BLUE, CYAN][i % 3]
            ax.plot(*points.T, color=color, alpha=.75, lw=1.1)
            all_coords.append(points)
            if track.get('animate'):
                marker, = ax.plot(*points[0].reshape(3,1), marker='o', color=color, markersize=5)
                self.extra_markers.append((marker, points))
        origins = np.asarray(visual.get('origins', []))
        if len(origins):
            ax.scatter(*origins.T, color=GOLD, s=35)
            all_coords.append(origins)
        if 'linkage' in visual:
            self.linkage = visual['linkage']
            self.link_artist, = ax.plot(*self.linkage[0].T, color=FG, lw=2, marker='o', markersize=5)
            all_coords.append(self.linkage.reshape(-1,3))
        points = coords.reshape(-1,1,3)
        collection = Line3DCollection(np.concatenate([points[:-1],points[1:]],axis=1),cmap=NEO_CMAP,linewidth=1.6)
        collection.set_array(parameter[:-1]);ax.add_collection3d(collection)
        together = np.vstack(all_coords)
        ranges=[]
        for j in range(3):
            lo, hi = np.min(together[:,j]), np.max(together[:,j])
            margin=max((hi-lo)*.09, max(abs(lo),abs(hi))*.01, 1e-4)
            ranges.append((lo-margin,hi+margin))
        spatial = self.result.config.model in {'pendulum','double_pendulum','projectile','orbit','em_particle','rutherford','two_body'}
        if spatial:
            width=max(hi-lo for lo,hi in ranges)
            ranges=[((lo+hi-width)/2,(lo+hi+width)/2) for lo,hi in ranges]
        ax.set_xlim(*ranges[0]);ax.set_ylim(*ranges[1]);ax.set_zlim(*ranges[2])
        ax.set_xlabel(visual['labels'][0],labelpad=5);ax.set_ylabel(visual['labels'][1],labelpad=5)
        ax.set_zlabel(visual['labels'][2],labelpad=5)
        ax.set_box_aspect((1,1,1) if spatial else (1,1,.85),zoom=1.03)
        self._draw_planes(ranges)
        self.marker, = ax.plot(*coords[0].reshape(3,1),marker='o',markersize=6,color=CYAN,markeredgecolor=FG)
        self.view('Perspectiva')

    def _draw_planes(self, ranges):
        x, y, z = [np.linspace(*r, 2) for r in ranges]
        xx, yy = np.meshgrid(x, y)
        self.plane_artists.append(self.ax.plot_surface(xx, yy, np.full_like(xx, z[0]), color=CYAN, alpha=.045))
        xx, zz = np.meshgrid(x, z)
        self.plane_artists.append(self.ax.plot_surface(xx, np.full_like(xx, y[-1]), zz, color=BLUE, alpha=.045))
        yy, zz = np.meshgrid(y, z)
        self.plane_artists.append(self.ax.plot_surface(np.full_like(yy, x[0]), yy, zz, color=GOLD, alpha=.035))
        self.show_planes(self.planes_visible)

    def show_planes(self, visible):
        self.planes_visible = visible
        for artist in self.plane_artists:
            artist.set_visible(visible)
        self.draw_idle()

    def view(self, name):
        if self.ax is None:
            return
        elev, azim = {"Perspectiva": (25, -55), "Plano XY": (90, -90),
                      "Plano XZ": (0, -90), "Plano YZ": (0, 0)}[name]
        self.ax.view_init(elev=elev, azim=azim)
        self.draw_idle()

    def set_frame(self, index):
        if self.marker is None:
            return
        point = self.coordinates[index]
        self.marker.set_data_3d([point[0]], [point[1]], [point[2]])
        for marker, points in self.extra_markers:
            marker.set_data_3d(*points[index].reshape(3,1))
        if self.link_artist is not None:
            self.link_artist.set_data_3d(*self.linkage[index].T)
        self.draw_idle()


class AnalysisCanvas(PlotCanvas):
    def draw_result(self, result):
        self.figure.clear()
        axes = self.figure.subplots(2, 2)
        a, b, d, e = axes.ravel()
        for ax in axes.ravel():
            style_axis(ax)
        if 'charts' in result.extra:
            self._draw_charts(axes.ravel(), result.extra['charts'])
            self.draw_idle()
            return
        c, y, t = result.config, result.states, result.t
        if c.model == "oscillator":
            a.plot(t, y[:, 0], color=CYAN, lw=1.4)
            a.set(xlabel="Tiempo (s)", ylabel="x (m)", title="Posición")
            b.plot(t, y[:, 1], color=BLUE, lw=1.2)
            b.set(xlabel="Tiempo (s)", ylabel="v (m/s)", title="Velocidad")
            d.plot(t, result.extra['energy'], color=GOLD, lw=1.4)
            d.set(xlabel="Tiempo (s)", ylabel="Energía (J)", title="Balance de energía")
            e.plot(y[:, 0], y[:, 1], color=CYAN, lw=1.1)
            e.set(xlabel="x (m)", ylabel="v (m/s)", title="Plano de fases")
        elif c.model == "lorenz":
            for ax, col, color, label in [(a, 0, CYAN, "x"), (b, 1, BLUE, "y"), (d, 2, GOLD, "z")]:
                ax.plot(t, y[:, col], color=color, lw=1.)
                ax.set(xlabel="Tiempo adimensional", ylabel=label, title=f"Evolución de {label}")
            e.semilogy(t, np.maximum(result.extra['separation'], 1e-16), color=GOLD, lw=1.)
            e.set(xlabel="Tiempo adimensional", ylabel="Distancia de estados", title="Sensibilidad inicial")
        else:
            extra = result.extra
            low, median, high = extra['quantiles']
            a.fill_between(t, low, high, color=BLUE, alpha=.22)
            a.plot(t, median, color=CYAN, lw=1.2)
            a.set(xlabel="Tiempo (s)", ylabel="x (m)", title="Percentiles 2.5–97.5 y mediana")
            b.hist(extra['terminal'], bins=35, color=BLUE, alpha=.8, edgecolor=BG)
            b.axvline(c.threshold, color=GOLD, lw=1.2)
            b.set(xlabel="Posición final (m)", ylabel="Realizaciones", title="Distribución final y umbral")
            d.scatter(extra['terminal'], extra['v_terminal'], c=extra['stiffness'],
                      cmap=NEO_CMAP, s=5, alpha=.45)
            d.set(xlabel="x final (m)", ylabel="v final (m/s)", title="Distribución conjunta de estados")
            n = np.arange(1, c.count+1)
            p = np.cumsum(extra['terminal'] > c.threshold)/n
            z = 1.959963984540054
            center = (p+z*z/(2*n))/(1+z*z/n)
            half = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
            e.fill_between(n, center-half, center+half, color=BLUE, alpha=.2)
            e.plot(n, p, color=CYAN, lw=1.)
            e.set(xlabel="Número de realizaciones", ylabel="Probabilidad", ylim=(0, 1),
                  title="Estimación y Wilson 95 % para cada N")
        self.draw_idle()

    def _draw_charts(self, axes, charts):
        colors=[CYAN,BLUE,GOLD,'#c8a0e1']
        for ax, spec in zip(axes,charts):
            if 'band' in spec:
                x,low,high=spec['band'];ax.fill_between(x,low,high,color=BLUE,alpha=.22)
            for i, series in enumerate(spec['series']):
                x,y=series['x'],series['y'];color=colors[i % len(colors)]
                kind=series.get('kind','line');label=series.get('label','')
                if kind=='scatter':ax.scatter(x,y,s=series.get('size',7),alpha=.65,color=color,label=label,rasterized=True)
                elif kind=='hist':ax.hist(x,bins=35,color=color,alpha=.8,label=label)
                elif kind=='bar':ax.bar(x,y,color=color,alpha=.75,label=label,width=.65)
                else:ax.plot(x,y,color=color,lw=1.1,label=label,linestyle=series.get('linestyle','-'))
            ax.set(xlabel=spec['xlabel'],ylabel=spec['ylabel'],title=spec['title'])
            ax.set_yscale(spec.get('yscale','linear'))
            if any(s.get('label') for s in spec['series']):
                legend=ax.legend(fontsize=7,facecolor=BG,edgecolor='#354f70')
                for text in legend.get_texts():text.set_color(FG)


class FormulaCanvas(PlotCanvas):
    def __init__(self):
        super().__init__(8, 4)
        self.setMinimumHeight(290)

    def draw_result(self, result):
        self.figure.clear()
        c = result.config
        if MODELS[c.model].formulas:
            formulas = MODELS[c.model].formulas
        elif c.model == "oscillator":
            formulas = [(r"$m\ddot{x}+c\dot{x}+kx=0$", "Ecuación del movimiento"),
                        (r"$\dot{x}=v,\quad \dot{v}=-(kx+cv)/m$", "Sistema integrado"),
                        (r"$E=\frac{1}{2}mv^2+\frac{1}{2}kx^2,\quad \frac{dE}{dt}=-cv^2$", "Energía y disipación"),
                        (r"$\omega_0=\sqrt{k/m},\quad \zeta=c/(2\sqrt{km})$", "Frecuencia natural y razón de amortiguamiento")]
        elif c.model == "lorenz":
            formulas = [(r"$\dot{x}=\sigma(y-x)$", "Dinámica de x"),
                        (r"$\dot{y}=x(\rho-z)-y$", "Dinámica de y"),
                        (r"$\dot{z}=xy-\beta z$", "Dinámica de z"),
                        (r"$d(t)=\|\mathbf{u}(t;\mathbf{u}_0+\delta\mathbf{e}_x)-\mathbf{u}(t;\mathbf{u}_0)\|_2$", "Sensibilidad inicial; no es un exponente de Lyapunov")]
        else:
            formulas = [(r"$K\sim U(\mu_k-\sqrt{3}s_k,\ \mu_k+\sqrt{3}s_k)$", "Rigidez aleatoria positiva"),
                        (r"$X_0\sim U(\mu_x-\sqrt{3}s_x,\ \mu_x+\sqrt{3}s_x),\quad K\perp X_0$", "Posición inicial independiente de la rigidez"),
                        (r"$\omega=\sqrt{K/m},\quad x(t)=X_0\cos(\omega t)+\frac{v_0}{\omega}\sin(\omega t)$", "Solución analítica; amortiguamiento c = 0"),
                        (r"$\hat p=\frac{1}{N}\sum_{i=1}^{N}\mathbb{1}[x_i(T)>a]$", "Probabilidad de superar el umbral a")]
        for index, (formula, label) in enumerate(formulas):
            y = .86-index*.235
            self.figure.text(.04, y, formula, fontsize=13 if len(formula)>100 else 15, color=CYAN)
            self.figure.text(.04, y-.075, label, fontsize=9, color=MUTED)
        self.draw_idle()
