# Dynamis 2.2.0

Programa nativo para Windows x64: **30 modelos, 68 ejemplos y nueve secciones**.

- Compton 3D: fotón, electrón, cuatro-momento y sección diferencial Klein–Nishina.
- Trampa de Paul: campo cuadrupolar RF, Mathieu y balance con trabajo de la fuente.
- Geometría: esfera, toro, Möbius y paraboloide paramétricos, área y refinamiento; geodésicas esféricas por rumbo.
- Grafos: mundo pequeño, Erdős–Rényi, geométricos y retícula; rutas mínimas, componentes, grados y agrupamiento.
- Difusión conservativa y osciladores sobre grafos, color animado, etiquetas, conectividad y modos normales.
- Controles para malla/aristas, etiquetas de nodos y nueve secciones; se conserva el neumorfismo azul marino y Computer Modern.
- Datos auxiliares exportables: cuatro-momentos, mallas, aristas/pesos, matrices, rutas, equilibrios y espectros.

Descarga **Dynamis.exe**: incluye Python y bibliotecas, para Windows x64. El ejecutable no está firmado.

65 pruebas de modelos e interfaz; la compilación verifica los 30 modelos, fuentes y figuras dentro del ejecutable. Los supuestos se detallan en la guía: Compton usa electrón libre en reposo, Paul es un cuadrupolo ideal, los barridos/mallas tienen resolución finita y las redes son modelos abstractos con unidades reducidas.

---

# Dynamis 2.1.0

Programa nativo de física para **Windows x64**, con 23 modelos y 52 ejemplos guiados. Diseño neumórfico oscuro azul marino, Space Grotesk y fórmulas/números con tipografía Computer Modern.

### Novedades

- **Partículas 3D:** gas de hasta 96 esferas con choques elásticos, presión en paredes y energía; hasta 128 cuerpos con gravedad o cargas eléctricas suavizadas, nube/disco, rotación y diagnósticos de conservación.
- **Sistemas dinámicos:** Rössler, Van der Pol, Lotka–Volterra, SIR, Hénon y Kuramoto. Condiciones vecinas, campos de direcciones y barridos de parámetros exportables.
- **Reproducción:** pausa, inicio, fotograma anterior/siguiente, velocidad y repetición.
- **Investigación:** trayectorias de todas las partículas, tablas de barridos, metadatos, notas, proyectos JSON y CSV/PNG. Se mantienen los modelos relativistas y cuánticos anteriores.
- **Ocho secciones:** Inicio, Laboratorio, Partículas 3D, Dinámica, Modelos, Catálogo, Resultados y Cuaderno.

### Descargar

Descarga **Dynamis.exe** y ábrelo en Windows x64. Python y las bibliotecas están incluidas. No necesita servidor ni navegador. El ejecutable no está firmado.

### Validación y alcance

53 pruebas automatizadas de modelos e interfaz. La compilación ejecuta el programa empaquetado con los 23 modelos y comprueba fuentes, figuras y secciones.

Los choques del gas se resuelven por subpasos con tiempos de contacto aproximados; N cuerpos usa potencial suavizado, unidades reducidas y comparación de paso. Los barridos son de horizonte finito y la distancia entre estados no es un exponente de Lyapunov. Los supuestos y las ecuaciones de cada modelo aparecen en el programa y en [la guía](https://github.com/Lumarri/fisica-dinamica/blob/main/docs/MODELOS.md).

- [Compilación y verificación en Windows](https://github.com/Lumarri/fisica-dinamica/actions/runs/42672570469)
- [Pruebas en Linux](https://github.com/Lumarri/fisica-dinamica/actions/runs/42672570731)
