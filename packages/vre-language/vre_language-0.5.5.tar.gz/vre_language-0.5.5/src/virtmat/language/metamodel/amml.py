"""processors for AMML objects"""
from virtmat.language.utilities.errors import raise_exception, StaticValueError
from virtmat.language.utilities.ase_params import spec, par_units


def amml_calculator_processor(obj):
    """apply constraints to amml calculator objects"""
    if obj.parameters:
        par_names = obj.parameters.get_column_names()
        if not all(p in par_units[obj.name] for p in par_names):
            inv_pars = tuple(p for p in par_names if p not in par_units[obj.name])
            msg = f'Invalid parameters used in calculator: {inv_pars}'
            raise_exception(obj.parameters, StaticValueError, msg)
    if obj.task:
        if obj.task not in spec[obj.name]['tasks']:
            msg = f'Task \"{obj.task}\" not supported in calculator \"{obj.name}\"'
            raise_exception(obj, StaticValueError, msg)
    modules = spec[obj.name].get('modulefiles') or {}
    modulefile = spec[obj.name].get('modulefile')
    if modulefile:
        ver = obj.pinning + obj.version if obj.pinning else modulefile['verspec']
        modules[modulefile['name']] = ver
    obj.resources = {'modules': modules, 'envs': spec[obj.name].get('envvars')}


def amml_algorithm_processor(obj):
    """apply constraints to amml algorithm objects"""
    if obj.name not in spec:
        msg = f'Algorithm {obj.name} is not implemented'
        raise_exception(obj, NotImplementedError, msg)
    params = spec[obj.name]['params']
    par_mandatory = [k for k, v in params.items() if 'default' not in v]
    mt1 = spec[obj.name].get('many_to_one')
    if mt1 is not None and obj.many_to_one is not mt1:
        msg = f'Incorrect many-to-one relationship for algorithm {obj.name}'
        raise_exception(obj, StaticValueError, msg)
    par_names = obj.parameters.get_column_names() if obj.parameters else []
    if not all(p in params for p in par_names):
        inv_pars = tuple(p for p in par_names if p not in params)
        msg = f'Invalid parameters used in algorithm {obj.name}: {inv_pars}'
        raise_exception(obj.parameters or obj, StaticValueError, msg)
    if not all(p in par_names for p in par_mandatory):
        inv_pars = tuple(p for p in par_mandatory if p not in par_names)
        msg = f'Mandatory parameters missing in algorithm {obj.name}: {inv_pars}'
        raise_exception(obj.parameters or obj, StaticValueError, msg)


def amml_property_processor(obj):
    """apply constraints to amml property objects"""
    if not (obj.calc or obj.algo):
        msg = 'property must include calculator or algorithm'
        raise_exception(obj, StaticValueError, msg)


def chem_term_processor(obj):
    """replace undefined coefficients with unity by convention"""
    if obj.coefficient is None:
        obj.coefficient = 1.0
