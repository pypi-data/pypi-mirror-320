"""unittests for code that is called only interactively"""
import pytest
from virtmat.language.utilities.textx import GrammarString, TextXCompleter
from virtmat.language.utilities.textx import display_exception
from virtmat.language.utilities.ase_handlers import get_ase_property
from virtmat.language.utilities.errors import PropertyError


@pytest.fixture(name='tab_completer')
def completer_func():
    """factory for completer objects"""
    options = ['%exit', '%bye']
    ids = ['bar', 'foo']
    return TextXCompleter(GrammarString().string, options, ids)


def test_completer(tab_completer):
    """test tab-completion"""
    assert '%exit' in tab_completer.complete('', 0)
    assert 'print' in tab_completer.complete('print', 0)
    assert '(' in tab_completer.complete('print', 0)
    assert 'print' in tab_completer.complete('print(', 0)
    assert 'print(bar' in tab_completer.matches
    tab_completer.complete('print(not ', 0)
    assert 'print(not true' in tab_completer.matches
    tab_completer.complete('a = ', 0)
    assert 'a = foo' in tab_completer.matches
    tab_completer.complete('x %%', 0)
    tab_completer.complete('%blah ', 0)
    assert tab_completer.complete('print(1)', 0) == 'print(1)'
    assert tab_completer.complete('print(a)', 0) == 'print(a)'


def test_display_exception(capsys):
    """test the display_exception() decorator function"""
    @display_exception
    def func_with_exception():
        raise RuntimeError()
    with pytest.raises(RuntimeError):
        func_with_exception()
    assert 'RuntimeError' in capsys.readouterr().err


def test_is_complete(tab_completer):
    """test is_complete() function"""
    assert tab_completer.is_complete('a = 3 +') is False
    assert tab_completer.is_complete('a = b +\n    4') is True
    assert tab_completer.is_complete('a = 3 +\n    4 +') is False
    assert tab_completer.is_complete('foo bar') is True
    assert tab_completer.is_complete('foo = bar') is True


def test_get_ase_property():
    """test get_ase_property function with exception"""
    msg = 'no property "magmoms" found for method "emt"'
    with pytest.raises(PropertyError, match=msg):
        get_ase_property('emt', 'magmoms', [])
