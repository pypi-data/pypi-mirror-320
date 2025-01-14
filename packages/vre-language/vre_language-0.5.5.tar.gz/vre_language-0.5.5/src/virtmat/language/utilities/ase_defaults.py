"""default values of parameters used in ASE calculators and algorithms"""
from virtmat.language.utilities.units import ureg

# at least one parameter default per calculator must be defined

calc_pars = {}

calc_pars['vasp'] = {
    'restart': None
}

calc_pars['turbomole'] = {
    'restart': False,
    'define_str': None,
    'control_kdg': None,
    'control_input': None,
    'reset_tolerance': ureg.Quantity(1e-2, 'angstrom')
}

# name 'lj' as accepted by get_calculator_class()
calc_pars['lj'] = {
    'sigma': ureg.Quantity(1.0, 'angstrom'),
    'epsilon': ureg.Quantity(1.0, 'eV')}

# name 'lennardjones' as returned by lj.LennardJones().name
calc_pars['lennardjones'] = calc_pars['lj']

calc_pars['emt'] = {
    'restart': None,
    'asap_cutoff': False
}

calc_pars['free_electrons'] = {
    'restart': None
}
