"""checks / constraints for AMML objects"""
from textx import get_children_of_type
from virtmat.language.utilities.errors import raise_exception, StaticValueError
from virtmat.language.utilities.textx import get_reference
from virtmat.language.utilities.ase_params import spec

task_properties = {
  'single point': ['energy', 'forces', 'dipole', 'stress', 'charges', 'magmom', 'magmoms'],
  'local minimum': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'global minimum': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'transition state': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'normal modes': ['vibrational_energies', 'energy_minimum', 'transition_state'],
  'micro-canonical': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'canonical': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'isothermal-isobaric': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'grand-canonical': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory']
}


def check_amml_property_processor(model, _):
    """check compatibility of properties with calculator task"""
    for obj in get_children_of_type('AMMLProperty', model):
        assert obj.calc or obj.algo
        algo = obj.algo and get_reference(obj.algo)
        calc = obj.calc and get_reference(obj.calc)
        calc_task = get_reference(obj.calc).task if obj.calc else ''
        calc_name = calc.name if calc else ''
        algo_name = algo.name if algo else ''
        if algo and calc:
            algo_task = spec[algo_name].get('calc_task')
            if algo_task and calc.task not in algo_task:
                message = (f'calculator task \"{calc.task}\" not compatible with '
                           f'algorithm \"{algo.name}\"')
                raise_exception(obj, StaticValueError, message)
        for name in obj.names:
            msg = (f'property \"{name}\" not available in algo \"{algo_name}\"'
                   f' or calc \"{calc_name}\"')
            if algo and name not in spec[algo_name]['properties']:
                if not calc or name not in spec[calc_name]['properties']:
                    raise_exception(obj, StaticValueError, msg)
            if calc and name not in spec[calc_name]['properties']:
                if not algo or name not in spec[algo_name]['properties']:
                    raise_exception(obj, StaticValueError, msg)
            if not algo and calc_task and name not in task_properties[calc_task]:
                msg = f'property \"{name}\" not available in task \"{calc_task}\"'
                raise_exception(obj, StaticValueError, msg)
