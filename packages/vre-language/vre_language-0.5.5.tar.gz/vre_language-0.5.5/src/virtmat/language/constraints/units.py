"""
check the units of specific quantities
"""
from textx import get_children
from virtmat.language.utilities.textx import isinstance_m
from virtmat.language.utilities.errors import textxerror_wrap, InvalidUnitError
from virtmat.language.utilities.units import ureg


@textxerror_wrap
def check_number_literal_units(obj, qname, unit):
    """check for invalid units in a number literal"""
    if obj.need_input:
        raise ValueError(f'{qname} must be a literal')
    test = ureg.Quantity(0, obj.inp_units)
    if str(test.to_base_units().units) != unit:
        raise InvalidUnitError(f'invalid unit of {qname}: {obj.inp_units}')


@textxerror_wrap
def check_units(obj, dimensionality):
    """check dimensionality of an object that has inp_units attribute"""
    assert hasattr(obj, 'inp_units')
    if not ureg.Quantity(1., obj.inp_units).check(dimensionality):
        msg = f'object must have dimensionality of {dimensionality}'
        raise InvalidUnitError(msg)


@textxerror_wrap
def parse_units(obj):
    """parse the units string to assure it is correct"""
    try:
        ureg.parse_units(obj.inp_units)
    except ValueError as err:
        if 'Unit expression cannot have a scaling factor' in str(err):
            raise InvalidUnitError(str(err)) from err
        raise err


def check_units_processor(model, _):
    """check units in all objects that have inp_units attribute"""
    classes = ('Quantity', 'PrintParameter', 'Series', 'IntArray', 'FloatArray',
               'ComplexArray')
    for obj in get_children(lambda x: isinstance_m(x, classes), model):
        if obj.inp_units is not None:
            parse_units(obj)
