"""Propiedades de referencia. Masas aproximadas de PDG y constantes de SciPy/CODATA."""
from dataclasses import dataclass
from scipy.constants import c, e, hbar, m_e, m_p, m_n, physical_constants

MEV_J = 1e6*e
HBAR_MEV_S = hbar/MEV_J


@dataclass(frozen=True)
class Particle:
    name: str
    mass_mev: float | None
    charge_e: float
    lifetime: float | None
    family: str
    structure: str
    source: str
    note: str = ''

    @property
    def mass_kg(self):
        if self.mass_mev is None:
            raise ValueError('No se ha fijado una masa para esta especie.')
        return self.mass_mev*MEV_J/c**2


PARTICLES = {
    'electron': Particle('Electrón e⁻', m_e*c*c/MEV_J, -1, None, 'Leptón', 'Elemental', 'CODATA / SciPy'),
    'positron': Particle('Positrón e⁺', m_e*c*c/MEV_J, 1, None, 'Antileptón', 'Elemental', 'CODATA / SciPy'),
    'muon': Particle('Muón μ⁻', 105.6583755, -1, 2.1969811e-6, 'Leptón', 'Elemental', 'PDG 2024'),
    'antimuon': Particle('Antimuón μ⁺', 105.6583755, 1, 2.1969811e-6, 'Antileptón', 'Elemental', 'PDG 2024'),
    'proton': Particle('Protón p', m_p*c*c/MEV_J, 1, None, 'Barión', 'Compuesto: uud', 'CODATA / SciPy'),
    'antiproton': Particle('Antiprotón p̄', m_p*c*c/MEV_J, -1, None, 'Antibarión', 'Compuesto', 'CODATA / SciPy'),
    'neutron': Particle('Neutrón n', m_n*c*c/MEV_J, 0, 878.4, 'Barión', 'Compuesto: udd', 'PDG 2024', 'Vida media libre aproximada; depende del promedio experimental.'),
    'pion': Particle('Pión π⁺', 139.57039, 1, 2.6033e-8, 'Mesón', 'Compuesto: u d̄', 'PDG 2024'),
    'pion_zero': Particle('Pión π⁰', 134.9768, 0, 8.43e-17, 'Mesón', 'Compuesto', 'PDG 2024'),
    'kaon': Particle('Kaón K⁺', 493.677, 1, 1.2380e-8, 'Mesón', 'Compuesto: u s̄', 'PDG 2024'),
    'photon': Particle('Fotón γ', 0., 0, None, 'Bosón gauge', 'Elemental', 'PDG', 'Masa en reposo nula; no tiene marco de reposo.'),
    'z_boson': Particle('Bosón Z⁰', 91187.6, 0, HBAR_MEV_S/2495.2, 'Bosón gauge', 'Elemental', 'PDG 2024', 'Vida media deducida de la anchura total aproximada de 2495.2 MeV.'),
    'alpha': Particle('Partícula α', physical_constants['alpha particle mass'][0]*c*c/MEV_J,
                      2, None, 'Núcleo', 'Compuesto: 2p + 2n', 'CODATA / SciPy'),
}
CHARGED_CHOICES = tuple((key, PARTICLES[key].name) for key in ['electron','positron','muon','antimuon','proton','antiproton','alpha'])


def relativistic_kinematics(kinetic_mev, mass_mev):
    """E, |p| y β en unidades naturales MeV, MeV/c y c; estable cerca de T=0."""
    import numpy as np
    if not np.isfinite([kinetic_mev, mass_mev]).all() or kinetic_mev < 0 or mass_mev <= 0:
        raise ValueError('La energía cinética no puede ser negativa y la masa debe ser positiva.')
    energy = kinetic_mev+mass_mev
    momentum = np.sqrt(kinetic_mev*(kinetic_mev+2*mass_mev))
    return energy, momentum, momentum/energy

# Tabla de consulta: los quarks no se ofrecen como proyectiles libres.
PARTICLES.update({
    'nu_e': Particle('Neutrino electrónico νₑ',None,0,None,'Leptón','Elemental','PDG','Estado de sabor: superposición de autoestados de masa; no se fija una masa en esta tabla.'),
    'nu_mu': Particle('Neutrino muónico νμ',None,0,None,'Leptón','Elemental','PDG','Estado de sabor; la masa nula en los ejemplos es una aproximación cinemática.'),
    'nu_tau': Particle('Neutrino tauónico ντ',None,0,None,'Leptón','Elemental','PDG','Estado de sabor; no se modelan oscilaciones de neutrinos en esta versión.'),
    'tau': Particle('Tau τ⁻',1776.86,-1,2.903e-13,'Leptón','Elemental','PDG 2024'),
    'antitau': Particle('Antitau τ⁺',1776.86,1,2.903e-13,'Antileptón','Elemental','PDG 2024'),
    'up': Particle('Quark u',2.16,2/3,None,'Quark','Elemental','PDG 2024 (aprox.)','Masa corriente MS-bar a 2 GeV; no es masa de una partícula libre.'),
    'down': Particle('Quark d',4.67,-1/3,None,'Quark','Elemental','PDG 2024 (aprox.)','Masa corriente MS-bar a 2 GeV; confinamiento.'),
    'strange': Particle('Quark s',93.4,-1/3,None,'Quark','Elemental','PDG 2024 (aprox.)','Masa corriente MS-bar a 2 GeV; confinamiento.'),
    'charm': Particle('Quark c',1270.,2/3,None,'Quark','Elemental','PDG 2024 (aprox.)','Masa MS-bar a su propia escala; confinamiento.'),
    'bottom': Particle('Quark b',4180.,-1/3,None,'Quark','Elemental','PDG 2024 (aprox.)','Masa MS-bar a su propia escala; confinamiento.'),
    'top': Particle('Quark t',172700.,2/3,None,'Quark','Elemental','PDG (aprox.)','Referencia redondeada; la definición y extracción de la masa dependen del esquema y método.'),
    'gluon': Particle('Gluón g',0.,0,None,'Bosón gauge','Elemental','Modelo Estándar','Representa ocho estados de color; no se observa aislado por confinamiento.'),
    'w_plus': Particle('Bosón W⁺',80370.,1,HBAR_MEV_S/2085.,'Bosón gauge','Elemental','PDG (aprox.)','Masa y anchura de referencia redondeadas; vida media deducida de Γ ≈ 2085 MeV.'),
    'w_minus': Particle('Bosón W⁻',80370.,-1,HBAR_MEV_S/2085.,'Bosón gauge','Elemental','PDG (aprox.)','Misma masa de referencia que W⁺.'),
    'higgs': Particle('Bosón de Higgs H',125200.,0,HBAR_MEV_S/4.1,'Bosón escalar','Elemental','PDG / Modelo Estándar (aprox.)','Vida deducida de una anchura de referencia del Modelo Estándar, Γ ≈ 4.1 MeV; no es una medición directa de vida media.'),
})
