"""Regenera la guía de estudio y los JSON de ejemplo desde el catálogo."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from catalog import MODELS,EXAMPLES
from experiments import example_config
from particle_data import PARTICLES


def cell(value):
    return str(value).replace('|',r'\|').replace('\n',' ')


def main():
    (ROOT/'docs').mkdir(exist_ok=True);(ROOT/'examples').mkdir(exist_ok=True)
    lines=['# Guía de modelos y ejemplos · DYNAMIS 2','',
           'Esta guía acompaña a las pestañas **Fórmulas y precisión**, **Datos** y **Guía y ejemplos** del programa.',
           f'Incluye {len(MODELS)} modelos y {len(EXAMPLES)} proyectos de ejemplo. El catálogo de referencia contiene {len(PARTICLES)} especies de partículas.',
           '', '## Uso de las unidades y de la precisión','',
           'Los rangos de cada campo no garantizan que todas sus combinaciones sean válidas. La aplicación comprueba también condiciones conjuntas. Las figuras son espaciales, de estados o complejas según indique cada modelo. En escenas espaciales se aplica la misma escala a los tres ejes.',
           '', 'Las integraciones numéricas usan DOP853 y una segunda solución refinada. Las comparaciones de tolerancia no garantizan el error global. Los modelos analíticos conservan las limitaciones de float64 y del muestreo de salida.',
           '', 'Los valores de referencia de partículas son nominales; no incluyen incertidumbres. Consulta PDG o CODATA para un trabajo experimental de precisión. Los quarks tienen masas dependientes del esquema y escala; a los estados de sabor de neutrinos no se les fija aquí una masa.', '']
    for index,(key,spec) in enumerate(MODELS.items(),1):
        lines += [f'## {index}. {spec.name}', '',f'**Área:** {spec.family}.', '',spec.summary,'',
                  '**Escena:** '+(spec.scene_note or 'Consulta los rótulos de los ejes: este modelo usa espacio de estados o espacio de fases ampliado.'),'',
                  ('**Duración:** '+str(spec.duration)+' '+spec.time_unit+f' por defecto; rango {spec.time_range[0]:g} a {spec.time_range[1]:g}.' if spec.timed else '**Variable de salida:** '+spec.time_unit+'. No se impone una duración temporal.'),'']
        if spec.parameters:
            lines += ['| Campo | Unidad | Valor por defecto | Rango / opciones | Significado |',
                      '| --- | --- | --- | --- | --- |']
            for parameter in spec.parameters:
                domain=', '.join(label for _,label in parameter.choices) if parameter.choices else f'{parameter.low:g} a {parameter.high:g}'
                default=dict(parameter.choices).get(parameter.default,parameter.default) if parameter.choices else parameter.default
                lines.append('| '+' | '.join(cell(x) for x in [parameter.label,parameter.unit or 'adimensional',default,domain,parameter.description])+' |')
            lines.append('')
        else:
            legacy={
                'oscillator':'m (kg), k (N/m), c (kg/s), x₀ (m), v₀ (m/s), duración (s), tolerancias y paso máximo.',
                'lorenz':'σ, ρ, β, x₀, y₀, z₀ y perturbación Δx adimensionales; duración y tolerancias.',
                'ensemble':'Masa (kg), rigidez media y desviación (N/m), posición media y desviación (m), v₀ (m/s), umbral (m), N, semilla y duración.'}
            lines+=['**Campos principales:** '+legacy[key],'']
        lines+=['### Supuestos','']+['- '+x for x in spec.assumptions]+['','### Preguntas para investigar','']+['- '+x for x in spec.questions]+['']
        if spec.formulas:
            lines+=['### Ecuaciones','']
            for formula,description in spec.formulas:
                lines += [description+':','', '$$'+formula.strip('$')+'$$','']
        lines+=['### Ejemplos','']
        for example in EXAMPLES:
            if example.model==key:
                lines+=['- ['+example.label+'](../examples/'+example.key+'.json): '+example.expected]
        lines+=['','### Referencias','']+['- ['+label+']('+url+')' for label,url in spec.references]+['']
    lines+=['## Condiciones adicionales y lectura de diagnósticos','',
        '- **Campo E/B:** límite de 2000 unidades del reloj interno para mantener una simulación interactiva. Reduce campos o tiempo si se supera. No se calculan radiación, colisiones ni pérdida por decaimiento de la partícula seguida.',
        '- **Rutherford:** K/(mc²) ≤ 0.05. La masa del blanco se considera infinita; A solo calcula un radio orientativo. Si el acercamiento llega al radio nuclear, el potencial puntual no basta para interpretar ese régimen.',
        '- **Dos cuerpos:** M ≥ m₁+m₂ y boost γ ≤ 10⁶. Se usan componentes de cono de luz para reducir cancelación numérica; reconstruir masas como E²−p² a boosts grandes puede perder precisión. El barrido angular no asigna una probabilidad de emisión.',
        '- **Decaimiento radiactivo:** el fondo integrado esperado se limita a 10¹² cuentas. Los intervalos de población son puntuales; al cambiar la resolución cambian los intervalos del detector.',
        '- **Barrera:** se limita la opacidad máxima a κa ≤ 300 para representar amplitudes con float64. El panel avisa si falta resolución espacial de la onda. La densidad es relativa y el cursor recorre posición, no tiempo.',
        '- **Mapa logístico:** debe quedar una órbita de al menos 50 iteraciones después del transitorio. El barrido de bifurcaciones usa 1000 iteraciones transitorias y conserva 100 por valor de r; la órbita seleccionada usa los valores configurados.',
        '- **Órbitas:** el centro es puntual, sin superficie ni colisiones. La energía es específica (J/kg). El paso máximo corresponde a τ=t√(GM/a³); la duración se expresa en períodos.',
        '- **Duffing:** la FFT usa la segunda mitad, quita la media y aplica ventana Hann. La sección estroboscópica usa interpolación lineal y descarta el primer 20 % del tiempo. Aumenta duración y resolución para investigar respuestas complejas.',
        '', '## Guardar y exportar','',
        'Los proyectos v2 guardan parámetros completos, unidades implícitas del modelo, semilla, tolerancias, nombre, investigador/a, objetivo, fuentes y notas. Se importan también proyectos v1. Los datos principales y auxiliares se eligen en la pestaña Datos; CSV exporta todas sus filas y un JSON asociado. Las figuras y fórmulas pueden guardarse en PNG.',
        '', 'Este archivo y los proyectos de ejemplo se regeneran con `python scripts/generate_manual.py`.','']
    (ROOT/'docs'/'MODELOS.md').write_text('\n'.join(lines),encoding='utf-8')
    for example in EXAMPLES:
        example_config(example.key).save(ROOT/'examples'/(example.key+'.json'))
    print(f'Guía y {len(EXAMPLES)} proyectos generados.')


if __name__=='__main__':main()
