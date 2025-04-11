import pytest
from typing import Any

from src.rustipy.option import Option, Some, NOTHING, is_some, is_nothing
from src.rustipy.result import Ok, Err
from tests.test_result import OK_VALUE

SOME_VALUE = 123
OTHER_VALUE = 456
DEFAULT_OPTION_VALUE = 0
SOME_STR_VALUE = "hello"
OTHER_STR_VALUE = "world"

class MyClass:
    def __init__(self, x: int):
        self.x = x
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MyClass):
            return NotImplemented
        return self.x == other.x
    def __repr__(self) -> str:
        return f"MyClass({self.x})"

# --- Helper Functions ---
def square(x: int) -> int:
    return x * x

def stringify(x: int) -> str:
    return str(x)

def check_positive(x: int) -> bool:
    return x > 0

def check_even(x: int) -> bool:
    return x % 2 == 0

def int_to_some_str(x: int) -> Option[str]:
    return Some(str(x))

def int_to_nothing_if_odd(x: int) -> Option[int]:
    if x % 2 == 0:
        return Some(x)
    else:
        return NOTHING

# --- Test Cases ---

# --- Basic Checks ---
def test_is_some():
    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING
    assert some.is_some() is True
    assert nothing.is_some() is False

def test_is_none():
    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING
    assert some.is_none() is False
    assert nothing.is_none() is True

def test_is_some_and():
    some_pos: Option[int] = Some(SOME_VALUE) # 123 > 0 -> True
    some_neg: Option[int] = Some(-10)       # -10 > 0 -> False
    nothing: Option[int] = NOTHING

    assert some_pos.is_some_and(check_positive) is True
    assert some_neg.is_some_and(check_positive) is False
    assert nothing.is_some_and(check_positive) is False

# --- Unwrapping ---
def test_unwrap():
    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING
    assert some.unwrap() == SOME_VALUE
    with pytest.raises(ValueError, match="Cannot unwrap a Nothing value."):
        nothing.unwrap()

def test_expect():
    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING
    assert some.expect("Value should be present") == SOME_VALUE
    with pytest.raises(ValueError, match="Custom error message"):
        nothing.expect("Custom error message")

def test_unwrap_or():
    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING
    assert some.unwrap_or(DEFAULT_OPTION_VALUE) == SOME_VALUE
    assert nothing.unwrap_or(DEFAULT_OPTION_VALUE) == DEFAULT_OPTION_VALUE

def test_unwrap_or_else():
    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING
    default_func = lambda: DEFAULT_OPTION_VALUE * 2

    assert some.unwrap_or_else(default_func) == SOME_VALUE
    assert nothing.unwrap_or_else(default_func) == DEFAULT_OPTION_VALUE * 2

# --- Mapping ---
def test_map():
    some: Option[int] = Some(SOME_VALUE) # 123
    nothing: Option[int] = NOTHING
    assert some.map(square) == Some(SOME_VALUE * SOME_VALUE) # Some(15129)
    assert nothing.map(square) == NOTHING

def test_map_or():
    some: Option[int] = Some(SOME_VALUE) # 123
    nothing: Option[int] = NOTHING
    default_str = "default"
    assert some.map_or(default_str, stringify) == str(SOME_VALUE) # "123"
    assert nothing.map_or(default_str, stringify) == default_str

def test_map_or_else():
    some: Option[int] = Some(SOME_VALUE) # 123
    nothing: Option[int] = NOTHING
    default_func = lambda: "computed_default"
    assert some.map_or_else(default_func, stringify) == str(SOME_VALUE) # "123"
    assert nothing.map_or_else(default_func, stringify) == "computed_default"

# --- Chaining / Combining ---
def test_and_then():
    some_even: Option[int] = Some(10)
    some_odd: Option[int] = Some(5)
    nothing: Option[int] = NOTHING

    assert some_even.and_then(int_to_some_str) == Some("10")
    assert some_odd.and_then(int_to_some_str) == Some("5")
    assert nothing.and_then(int_to_some_str) == NOTHING

    assert some_even.and_then(int_to_nothing_if_odd) == Some(10)
    assert some_odd.and_then(int_to_nothing_if_odd) == NOTHING
    assert nothing.and_then(int_to_nothing_if_odd) == NOTHING

def test_and_():
    s1: Option[int] = Some(SOME_VALUE)
    s2: Option[str] = Some(SOME_STR_VALUE)
    n1: Option[int] = NOTHING
    n2: Option[str] = NOTHING

    assert s1.and_(s2) == s2
    assert s1.and_(n2) == n2
    assert n1.and_(s2) == n1 # Returns self (Nothing)
    assert n1.and_(n2) == n1 # Returns self (Nothing)

def test_or_():
    s1: Option[int] = Some(SOME_VALUE)
    s2: Option[int] = Some(OTHER_VALUE)
    n1: Option[int] = NOTHING
    n2: Option[int] = NOTHING

    assert s1.or_(s2) == s1
    assert s1.or_(n1) == s1
    assert n1.or_(s2) == s2
    assert n1.or_(n2) == n2 # which is NOTHING

def test_or_else():
    s1: Option[int] = Some(SOME_VALUE)
    n1: Option[int] = NOTHING
    default_some_func = lambda: Some(DEFAULT_OPTION_VALUE)
    default_nothing_func = lambda: NOTHING

    assert s1.or_else(default_some_func) == s1
    assert s1.or_else(default_nothing_func) == s1
    assert n1.or_else(default_some_func) == Some(DEFAULT_OPTION_VALUE)
    assert n1.or_else(default_nothing_func) == NOTHING

def test_xor():
    s1: Option[int] = Some(SOME_VALUE)
    s2: Option[int] = Some(OTHER_VALUE)
    n1: Option[int] = NOTHING
    n2: Option[int] = NOTHING # Same as n1

    assert s1.xor(s2) == NOTHING # Some ^ Some -> Nothing
    assert s1.xor(n1) == s1      # Some ^ Nothing -> Some
    assert n1.xor(s2) == s2      # Nothing ^ Some -> Some
    assert n1.xor(n2) == NOTHING # Nothing ^ Nothing -> Nothing

def test_zip():
    s1: Option[int] = Some(SOME_VALUE) # 123
    s2: Option[str] = Some(SOME_STR_VALUE) # "hello"
    n1: Option[int] = NOTHING
    n2: Option[str] = NOTHING

    assert s1.zip(s2) == Some((SOME_VALUE, SOME_STR_VALUE)) # Some((123, "hello"))
    assert s1.zip(n2) == NOTHING
    assert n1.zip(s2) == NOTHING
    assert n1.zip(n2) == NOTHING

# --- Filtering ---
def test_filter():
    s_even: Option[int] = Some(10)
    s_odd: Option[int] = Some(5)
    n: Option[int] = NOTHING

    assert s_even.filter(check_even) == Some(10)
    assert s_odd.filter(check_even) == NOTHING
    assert n.filter(check_even) == NOTHING

    assert s_even.filter(lambda x: x > 5) == Some(10)
    assert s_odd.filter(lambda x: x > 5) == NOTHING

# --- Conversion to Result ---
def test_ok_or():
    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING
    err_val = "Is Nothing"

    # Use explicit types for Ok/Err comparison due to potential inference issues
    assert some.ok_or(err_val) == Ok[int, str](SOME_VALUE)
    assert nothing.ok_or(err_val) == Err[Any, str](err_val) # T becomes Any for Err

def test_ok_or_else():
    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING
    err_func = lambda: "Computed Error"

    # Use explicit types for Ok/Err comparison
    assert some.ok_or_else(err_func) == Ok[int, str](SOME_VALUE)
    assert nothing.ok_or_else(err_func) == Err[Any, str]("Computed Error") # T becomes Any

# --- Inspection/Other ---
def test_inspect():
    inspected_val = None
    def inspector(x: int):
        nonlocal inspected_val
        inspected_val = x * 2

    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING

    assert some.inspect(inspector) is some # Returns self
    assert inspected_val == SOME_VALUE * 2

    inspected_val = None # Reset
    assert nothing.inspect(inspector) is nothing # Returns self
    assert inspected_val is None

def test_take():
    # Note: This tests the non-mutating version described in the source comment
    some: Option[int] = Some(SOME_VALUE)
    nothing: Option[int] = NOTHING

    taken_some = some.take()
    assert taken_some == Some(SOME_VALUE)
    assert some == Some(SOME_VALUE) # Original is unchanged

    taken_nothing = nothing.take()
    assert taken_nothing == NOTHING
    assert nothing == NOTHING # Original is unchanged

def test_contains():
    # Assuming contains was kept in Option implementation
    some: Option[int] = Some(SOME_VALUE)
    some_other: Option[int] = Some(OTHER_VALUE)
    nothing: Option[int] = NOTHING

    assert some.contains(SOME_VALUE) is True
    assert some.contains(OTHER_VALUE) is False
    assert some_other.contains(SOME_VALUE) is False
    assert nothing.contains(SOME_VALUE) is False
    assert nothing.contains(None) is False # Check None specifically

# --- Equality and Representation ---
def test_equality():
    assert Some(10) == Some(10)
    assert Some(10) != Some(20)
    assert Some([1]) == Some([1])
    assert Some([1]) != Some([2])
    assert NOTHING == NOTHING
    assert Some(10) != NOTHING
    assert NOTHING != Some(10)
    assert Some(None) == Some(None) # Test Some(None) equality
    assert Some(None) != NOTHING
    assert NOTHING != Some(None)
    assert Some(MyClass(1)) == Some(MyClass(1))
    assert Some(MyClass(1)) != Some(MyClass(2))
    assert Some(10) != 10 # type: ignore
    assert NOTHING != None # type: ignore

def test_repr():
    assert repr(Some(10)) == "Some(10)"
    assert repr(Some("hello")) == "Some('hello')"
    assert repr(Some([1, 2])) == "Some([1, 2])"
    assert repr(NOTHING) == "Nothing"
    assert repr(Some(None)) == "Some(None)" # Test Some(None) repr
    assert repr(Some(MyClass(5))) == "Some(MyClass(5))"

# --- Type Guards ---
def test_type_guards():
    some: Option[int] = Some(OK_VALUE)
    nothing: Option[int] = NOTHING

    if is_some(some):
        assert some.unwrap() == OK_VALUE
    else:
        pytest.fail("is_some failed for Some value")

    if is_nothing(some):
        pytest.fail("is_nothing succeeded for Some value")

    if is_some(nothing):
        pytest.fail("is_some succeeded for Nothing value")

    if is_nothing(nothing):
        # Can't unwrap Nothing, just check identity
        assert nothing is NOTHING
    else:
        pytest.fail("is_nothing failed for Nothing value")

# --- Tests for Various Types ---
def test_option_with_none_value():
    # Test creating Some(None) and its interactions
    some_none: Option[int | None] = Some(None) # T is Optional[int]
    # nothing: Option[int | None] = NOTHING

    assert some_none.is_some() is True
    assert some_none.unwrap() is None
    assert some_none.map(lambda x: x is None) == Some(True)
    assert some_none.unwrap_or(DEFAULT_OPTION_VALUE) is None # Returns inner None
    assert some_none.ok_or("Error") == Ok[int | None, str](None)
    assert some_none.contains(None) is True # Should contain None
    assert some_none.contains(0) is False

    # Check filter behavior with None
    assert some_none.filter(lambda x: x is None) == Some(None)
    assert some_none.filter(lambda x: x is not None) == NOTHING

def test_option_with_mutable_value():
    original_list = [10, 20]
    some_list: Option[list[int]] = Some(original_list)

    assert some_list.unwrap() is original_list

    # Map creates a new Option with a new list (depending on lambda)
    mapped = some_list.map(lambda x: x + [30])
    assert mapped == Some([10, 20, 30])
    assert original_list == [10, 20] # Original unchanged if lambda didn't mutate

    # Inspect allows mutation
    def append_40(l: list[int]):
        l.append(40)
    some_list.inspect(append_40)
    assert original_list == [10, 20, 40]
    assert some_list.unwrap() == [10, 20, 40]

    # Contains checks equality
    assert some_list.contains([10, 20, 40]) is True
    assert some_list.contains([10, 20]) is False

def test_option_with_custom_class():
    obj = MyClass(99)
    some_obj: Option[MyClass] = Some(obj)
    nothing: Option[MyClass] = NOTHING

    assert some_obj.unwrap() is obj
    assert some_obj.map(lambda o: o.x) == Some(99)
    assert some_obj.filter(lambda o: o.x > 0) == Some(obj)
    assert some_obj.filter(lambda o: o.x < 0) == NOTHING
    assert nothing.unwrap_or(MyClass(0)) == MyClass(0)
    assert some_obj.contains(MyClass(99)) is True

