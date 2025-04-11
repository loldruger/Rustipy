from typing import Any
import pytest

# Assuming your code is in src/rustipy/
# Adjust the import path if your structure is different
# Removed ResultBase, OptionBase from imports
from src.rustipy.result import Ok, Err, Result, is_ok, is_err
from src.rustipy.option import Some, NOTHING, Option

# --- Test Data ---
OK_VALUE = 100
ERR_VALUE = "Error occurred"
OTHER_OK_VALUE = 200
OTHER_ERR_VALUE = "Another error"
DEFAULT_VALUE = 0
# DEFAULT_ERR = "Default Error" # Unused variable removed

# --- Helper Classes for Testing (Type hints added) ---
class MyClass:
    # Assuming x is int based on usage in tests
    def __init__(self, x: int):
        self.x = x
    def __eq__(self, other: object) -> bool:
        # isinstance check is good practice for __eq__
        if not isinstance(other, MyClass):
            return NotImplemented
        return self.x == other.x
    def __repr__(self) -> str:
        return f"MyClass({self.x})"

class MyError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg) # Call parent constructor
        self.msg = msg
    def __eq__(self, other: object) -> bool:
        # isinstance check is good practice for __eq__
        if not isinstance(other, MyError):
            return NotImplemented
        return self.msg == other.msg
    def __repr__(self) -> str:
        return f"MyError('{self.msg}')"

# --- Helper Functions (Return types changed to Result) ---
def square(x: int) -> int:
    return x * x

def stringify(x: int) -> str:
    return str(x)

def len_str(s: str) -> int:
    return len(s)

def check_positive(x: int) -> bool:
    return x > 0

def check_contains_error(s: str) -> bool:
    # Ensure case-insensitivity
    return "error" in str(s).lower()

# Return type changed ResultBase -> Result
def ok_if_positive(x: int) -> Result[int, str]:
    if x > 0:
        return Ok(x)
    else:
        return Err("Not positive")

# Return type changed ResultBase -> Result
def err_if_negative(x: int) -> Result[int, str]:
    if x < 0:
        return Err("Is negative")
    else:
        return Ok(x)

def err_to_str(e: str) -> str:
    return f"Error: {e}"

# Return type changed ResultBase -> Result
def err_to_default_ok(e: str) -> Result[int, str]:
    return Ok(DEFAULT_VALUE)

# Return type changed ResultBase -> Result
def err_to_other_err(e: str) -> Result[int, str]:
    return Err(OTHER_ERR_VALUE)

# def ok_to_str(x: int) -> str: # Unused function removed
#     return f"Value: {x}"

# --- Test Cases ---

# --- Basic Checks ---
def test_is_ok():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.is_ok() is True
    assert err_res.is_ok() is False

def test_is_err():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.is_err() is False
    assert err_res.is_err() is True

def test_is_ok_and():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    ok_neg_res: Result[int, str] = Ok(-5)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.is_ok_and(check_positive) is True
    assert ok_neg_res.is_ok_and(check_positive) is False
    assert err_res.is_ok_and(check_positive) is False

def test_is_err_and():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    err_other: Result[int, str] = Err("Something else")
    assert ok_res.is_err_and(check_contains_error) is False
    assert err_res.is_err_and(check_contains_error) is True
    assert err_other.is_err_and(check_contains_error) is False

# --- Conversion to Option ---
def test_ok_method():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.ok() == Some(OK_VALUE)
    assert err_res.ok() == NOTHING

def test_err_method():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.err() == NOTHING
    assert err_res.err() == Some(ERR_VALUE)

# --- Mapping ---
def test_map():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.map(square) == Ok(OK_VALUE * OK_VALUE)
    assert err_res.map(square) == Err(ERR_VALUE)

def test_map_err():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.map_err(len_str) == Ok(OK_VALUE)
    assert err_res.map_err(len_str) == Err(len(ERR_VALUE))

def test_map_or():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.map_or("default", stringify) == str(OK_VALUE)
    assert err_res.map_or("default", stringify) == "default"

def test_map_or_else():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.map_or_else(lambda e: f"Err: {len(e)}", stringify) == str(OK_VALUE)
    assert err_res.map_or_else(lambda e: f"Err: {len(e)}", stringify) == f"Err: {len(ERR_VALUE)}"

def test_map_or_default():
    err_res: Result[int, str] = Err(ERR_VALUE)

    with pytest.raises(NotImplementedError):
        err_res.map_or_default(stringify)

    ok_int_res: Result[int, str] = Ok(5)
    err_int_res: Result[int, str] = Err("error")
    assert ok_int_res.map_or_default(square) == 25 # Assuming implementation exists

    with pytest.raises(NotImplementedError):
        err_int_res.map_or_default(square)


# --- Inspection ---
def test_inspect():
    inspected_ok = None
    def inspect_ok_fn(x: int):
        nonlocal inspected_ok
        inspected_ok = x

    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert ok_res.inspect(inspect_ok_fn) is ok_res
    assert inspected_ok == OK_VALUE

    inspected_ok = None
    assert err_res.inspect(inspect_ok_fn) is err_res
    assert inspected_ok is None

def test_inspect_err():
    inspected_err = None
    def inspect_err_fn(e: str):
        nonlocal inspected_err
        inspected_err = e

    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert ok_res.inspect_err(inspect_err_fn) is ok_res
    assert inspected_err is None

    inspected_err = None
    assert err_res.inspect_err(inspect_err_fn) is err_res
    assert inspected_err == ERR_VALUE

# --- Unwrapping and Expecting ---
def test_expect():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.expect("Should be Ok") == OK_VALUE
    with pytest.raises(ValueError, match=f"Custom error: '{ERR_VALUE}'"):
        err_res.expect("Custom error")

def test_unwrap():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.unwrap() == OK_VALUE
    with pytest.raises(ValueError, match=f"Called unwrap on an Err value: '{ERR_VALUE}'"):
        err_res.unwrap()

def test_expect_err():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert err_res.expect_err("Should be Err") == ERR_VALUE
    with pytest.raises(ValueError, match=f"Custom error: {OK_VALUE}"):
        ok_res.expect_err("Custom error")

def test_unwrap_err():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert err_res.unwrap_err() == ERR_VALUE
    with pytest.raises(ValueError, match=f"Called unwrap_err on an Ok value: {OK_VALUE}"):
        ok_res.unwrap_err()

def test_unwrap_or():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.unwrap_or(DEFAULT_VALUE) == OK_VALUE
    assert err_res.unwrap_or(DEFAULT_VALUE) == DEFAULT_VALUE

def test_unwrap_or_else():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.unwrap_or_else(len_str) == OK_VALUE
    assert err_res.unwrap_or_else(len_str) == len(ERR_VALUE)

def test_unwrap_or_default():
    ok_int_res: Result[int, str] = Ok(OK_VALUE)
    err_int_res: Result[int, str] = Err(ERR_VALUE)
    ok_str_res: Result[str, int] = Ok("hello")
    err_str_res: Result[str, int] = Err(5)

    assert ok_int_res.unwrap_or_default() == OK_VALUE
    assert ok_str_res.unwrap_or_default() == "hello"

    with pytest.raises(NotImplementedError):
        err_int_res.unwrap_or_default()
    with pytest.raises(NotImplementedError):
        err_str_res.unwrap_or_default()

# --- Chaining Operations ---
def test_and_then():
    ok_pos: Result[int, str] = Ok(5)
    ok_neg: Result[int, str] = Ok(-5)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert ok_pos.and_then(ok_if_positive) == Ok(5)
    assert ok_neg.and_then(ok_if_positive) == Err("Not positive")
    assert err_res.and_then(ok_if_positive) == Err(ERR_VALUE)

def test_or_else():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_orig: Result[int, str] = Err(ERR_VALUE)
    err_neg: Result[int, str] = Err("negative")

    assert ok_res.or_else(err_to_default_ok) == Ok(OK_VALUE)
    assert ok_res.or_else(err_to_other_err) == Ok(OK_VALUE)

    assert err_orig.or_else(err_to_default_ok) == Ok(DEFAULT_VALUE)
    assert err_orig.or_else(err_to_other_err) == Err(OTHER_ERR_VALUE)

    assert err_neg.or_else(err_to_default_ok) == Ok(DEFAULT_VALUE)
    assert err_neg.or_else(err_to_other_err) == Err(OTHER_ERR_VALUE)


def test_and_():
    ok1: Result[int, str] = Ok(OK_VALUE)
    ok2: Result[str, str] = Ok("World")
    err1: Result[int, str] = Err(ERR_VALUE)
    err2: Result[str, str] = Err(OTHER_ERR_VALUE)

    assert ok1.and_(ok2) == Ok("World")
    assert ok1.and_(err2) == Err(OTHER_ERR_VALUE)
    assert err1.and_(ok2) == Err(ERR_VALUE)
    assert err1.and_(err2) == Err(ERR_VALUE)

def test_or_():
    ok1: Result[int, str] = Ok(OK_VALUE)
    ok2: Result[int, str] = Ok(OTHER_OK_VALUE)
    err1: Result[int, str] = Err(ERR_VALUE)
    err2: Result[int, int] = Err(999) # Different Error type F

    assert ok1.or_(ok2) == Ok(OK_VALUE)
    assert ok1.or_(err2) == Ok(OK_VALUE)
    assert err1.or_(ok2) == Ok(OTHER_OK_VALUE)
    assert err1.or_(err2) == Err(999)

# --- Iteration ---
def test_iter():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    ok_list = list(ok_res.iter())
    err_list = list(err_res.iter())

    assert ok_list == [OK_VALUE]
    assert err_list == []

def test_iter_mut():
    # Test with mutable value
    mutable_val = [1, 2]
    ok_res_mut: Result[list[int], str] = Ok(mutable_val)
    err_res_mut: Result[list[int], str] = Err(ERR_VALUE)

    ok_iter_mut = ok_res_mut.iter_mut()
    try:
        val_ref = next(ok_iter_mut)
        assert val_ref is mutable_val
        val_ref.append(3)
    except StopIteration:
        pytest.fail("Iterator for Ok (mutable) should yield one value")

    assert mutable_val == [1, 2, 3]
    assert ok_res_mut.unwrap() == [1, 2, 3]

    err_iter_mut = err_res_mut.iter_mut()
    with pytest.raises(StopIteration):
        next(err_iter_mut)

    # Test with immutable value
    ok_res_imm: Result[int, str] = Ok(OK_VALUE)
    err_res_imm: Result[int, str] = Err(ERR_VALUE)

    ok_iter_imm = ok_res_imm.iter_mut()
    try:
        val_ref_imm = next(ok_iter_imm)
        assert val_ref_imm == OK_VALUE
    except StopIteration:
        pytest.fail("Iterator for Ok (immutable) should yield one value")

    with pytest.raises(StopIteration):
        next(ok_iter_imm)

    err_iter_imm = err_res_imm.iter_mut()
    with pytest.raises(StopIteration):
        next(err_iter_imm)


# --- Flattening and Transposing ---
def test_flatten():
    ok_ok: Result[Result[int, str], str] = Ok(Ok(OK_VALUE))
    ok_err: Result[Result[int, str], str] = Ok(Err(ERR_VALUE))
    err_outer: Result[Result[int, str], str] = Err(OTHER_ERR_VALUE)
    ok_not_result: Result[int, str] = Ok(123)

    assert ok_ok.flatten() == Ok(OK_VALUE)
    assert ok_err.flatten() == Err(ERR_VALUE)
    assert err_outer.flatten() == Err(OTHER_ERR_VALUE)

    with pytest.raises(TypeError):
        ok_not_result.flatten()

def test_transpose():
    ok_some: Result[Option[int], str] = Ok(Some(OK_VALUE))
    ok_nothing: Result[Option[int], str] = Ok(NOTHING)
    err_res: Result[Option[int], str] = Err(ERR_VALUE)
    ok_not_option: Result[int, str] = Ok(123)

    # Type checker might struggle here, add ignores if necessary
    assert ok_some.transpose() == Some(Ok(OK_VALUE)) # type: ignore
    assert ok_nothing.transpose() == NOTHING
    assert err_res.transpose() == Some(Err(ERR_VALUE)) # type: ignore

    with pytest.raises(TypeError):
        ok_not_option.transpose()

# --- Consuming Operations (Conceptual) ---
def test_into_ok():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert ok_res.into_ok() == OK_VALUE
    assert ok_res.is_ok()

    with pytest.raises(ValueError, match=f"Called into_ok on an Err value: '{ERR_VALUE}'"):
        err_res.into_ok()

def test_into_err():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert err_res.into_err() == ERR_VALUE
    assert err_res.is_err()

    with pytest.raises(ValueError, match=f"Called into_err on an Ok value: {OK_VALUE}"):
        ok_res.into_err()

# --- Copying and Cloning ---
def test_cloned():
    original_list = [1, 2]
    ok_res: Result[list[int], str] = Ok(original_list)
    err_res: Result[int, list[int]] = Err(original_list)

    cloned_ok = ok_res.cloned()
    assert cloned_ok == ok_res
    assert cloned_ok.unwrap() is not original_list
    cloned_ok.unwrap().append(3)
    assert original_list == [1, 2]

    cloned_err = err_res.cloned()
    assert cloned_err == err_res
    assert cloned_err.unwrap_err() is not original_list
    cloned_err.unwrap_err().append(3)
    assert original_list == [1, 2]

def test_copied():
    original_list = [1, 2]
    ok_res: Result[list[int], str] = Ok(original_list)
    err_res: Result[int, list[int]] = Err(original_list)

    copied_ok = ok_res.copied()
    assert copied_ok == ok_res
    assert copied_ok.unwrap() is not original_list

    copied_ok.unwrap().append(3)
    assert original_list == [1, 2]

    copied_err = err_res.copied()
    assert copied_err == err_res
    assert copied_err.unwrap_err() is not original_list
    copied_err.unwrap_err().append(3)
    assert original_list == [1, 2]

# --- References (Conceptual in Python) ---
def test_as_ref():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.as_ref() is ok_res
    assert err_res.as_ref() is err_res

def test_as_mut():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.as_mut() is ok_res
    assert err_res.as_mut() is err_res

# --- Equality and Representation ---
def test_equality():
    assert Ok(10) == Ok(10)
    assert Ok(10) != Ok(20)
    assert Err("abc") == Err("abc")
    assert Err("abc") != Err("def")
    assert Ok(10) != Err(10)
    assert Ok(10) != Err("abc")
    assert Ok([1]) == Ok([1])
    assert Ok([1]) != Ok([2])
    assert Err([1]) == Err([1])
    assert Err([1]) != Err([2])
    assert Ok(10) != 10 # type: ignore
    assert Err("a") != "a" # type: ignore
    assert Ok(None) == Ok(None)
    assert Err(None) == Err(None)
    assert Ok(None) != Ok(0)
    assert Err(None) != Err(0)
    assert Ok(MyClass(1)) == Ok(MyClass(1))
    assert Ok(MyClass(1)) != Ok(MyClass(2))
    assert Err(MyError("a")) == Err(MyError("a"))
    assert Err(MyError("a")) != Err(MyError("b"))

# def test_repr():
#     assert repr(Ok(10)) == "Ok(10)"
#     assert repr(Err("error")) == "Err('error')"
#     assert repr(Ok("hello")) == "Ok('hello')"
#     assert repr(Err(None)) == "Err(None)"
#     assert repr(Ok([1, 2])) == "Ok([1, 2])"
#     assert repr(Ok(MyClass(5))) == "Ok(MyClass(5))"
#     assert repr(Err(MyError("fail"))) == "Err(MyError('fail'))"


# --- Type Guards ---
def test_type_guards():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    if is_ok(ok_res):
        assert ok_res.unwrap() == OK_VALUE
    else:
        pytest.fail("is_ok failed for Ok value")

    if is_err(ok_res):
        pytest.fail("is_err succeeded for Ok value")

    if is_ok(err_res):
        pytest.fail("is_ok succeeded for Err value")

    if is_err(err_res):
        assert err_res.unwrap_err() == ERR_VALUE
    else:
        pytest.fail("is_err failed for Err value")

def test_ok_none():
    res: Result[None, str] = Ok(None)
    assert res.is_ok() is True
    assert res.unwrap() is None
    assert res.ok() == Some(None)
    assert res.err() == NOTHING
    assert res.map(lambda x: x is None) == Ok(True)
    assert res.unwrap_or(None) is None
    assert res.expect("Should be Ok(None)") is None

def test_err_none():
    res: Result[int, None] = Err(None)
    assert res.is_err() is True
    assert res.unwrap_err() is None
    assert res.ok() == NOTHING
    assert res.err() == Some(None)
    assert res.map_err(lambda x: x is None) == Err(True)
    assert res.unwrap_or(DEFAULT_VALUE) == DEFAULT_VALUE
    with pytest.raises(ValueError):
        res.unwrap()
    assert res.expect_err("Should be Err(None)") is None

def test_mutable_value_ok():
    # Add specific type hint for d
    d: dict[str, int] = {'a': 1}
    # Use specific dict type in Result annotation
    res: Result[dict[str, int], str] = Ok(d)
    assert res.unwrap() is d
    # Use specific dict type in comparison value and Ok type args
    assert res == Ok[dict[str, int], Any]({'a': 1})

    # Use specific dict type in map result comparison
    # Lambda implicitly creates dict[str, int]
    mapped = res.map(lambda x: {**x, 'b': 2})
    assert mapped == Ok[dict[str, int], str]({'a': 1, 'b': 2})

    # Use specific dict type in helper signature
    def add_c_if_a_exists(x: dict[str, int]) -> Result[dict[str, int], str]:
        # Add specific type hint for new_d
        new_d: dict[str, int] = x.copy() # Copy is made
        if 'a' in new_d:
            new_d['c'] = 3
            # Use specific dict type in Ok return type args
            return Ok[dict[str, int], str](new_d)
        else:
            # Use specific dict type in Err return type args
            return Err[dict[str, int], str]("No 'a'")
    chained = res.and_then(add_c_if_a_exists)
    # Use specific dict type in comparison value and Ok type args
    assert chained == Ok[dict[str, int], str]({'a': 1, 'c': 3})
    # Original dict 'd' was NOT mutated because the helper worked on a copy.
    assert d == {'a': 1}

def test_mutable_value_err():
    # Add specific type hint for l
    l: list[str] = ['error', 'list']
    # Use specific list type in Result annotation
    res: Result[int, list[str]] = Err(l)
    assert res.unwrap_err() is l
    # Use specific list type in comparison value and Err type args
    assert res == Err[Any, list[str]](['error', 'list'])

    # Test map_err - avoid mutating original list in helper
    # Lambda implicitly creates list[str]
    mapped = res.map_err(lambda x: x + ['!'])
    # Use specific list type in comparison value and Err type args
    assert mapped == Err[int, list[str]](['error', 'list', '!'])
    # Original list should remain unchanged
    assert l == ['error', 'list']

    # Use specific list type for re-creation
    res = Err[int, list[str]](l) # Recreate Err with original list
    # Lambda input type inferred, Ok return type specified
    chained = res.or_else(lambda e: Ok[int, Any](len(e))) # Explicit type
    assert chained == Ok[int, Any](2) # Explicit type

def test_custom_class_ok():
    obj = MyClass(123)
    res: Result[MyClass, str] = Ok(obj)
    assert res.is_ok()
    assert res.unwrap() == MyClass(123)
    assert res.unwrap() is obj
    assert res.map(lambda o: o.x * 2) == Ok(246)
    # contains test removed

def test_custom_class_err():
    err_obj = MyError("Failed")
    res: Result[int, MyError] = Err(err_obj)
    assert res.is_err()
    assert res.unwrap_err() == MyError("Failed")
    assert res.unwrap_err() is err_obj
    assert res.map_err(lambda e: MyError(e.msg + "!")) == Err(MyError("Failed!"))
    # contains_err test removed

def test_exception_error():
    err_val = ValueError("Invalid input")
    res: Result[int, ValueError] = Err(err_val) # T=int, E=ValueError
    assert res.is_err()
    assert res.unwrap_err() is err_val
    # assert res.map_err(lambda e: str) == Err[int, str]("Invalid input")
    assert res.or_else(lambda e: Ok[int, Any](0)) == Ok[int, Any](0)

def test_chaining_ok_path():
    res = (
        Ok(5)
            .map(square)
            .and_then(ok_if_positive)
            .or_else(err_to_default_ok)
            .map_err(len_str)
            .unwrap_or(DEFAULT_VALUE)
    ) 
    assert res == 25

def test_chaining_err_path():
    res = (
        Ok(-5)
            .map(square)
            .and_then(ok_if_positive) # Ok(25)
            .and_then(err_if_negative) # Ok(25)
            .and_then(lambda x: Err("Force Err")) # Err("Force Err")
            .or_else(err_to_default_ok) # Ok(DEFAULT_VALUE)
            .unwrap()
    )
    assert res == DEFAULT_VALUE

def test_chaining_early_err():
    res = (
        Err(ERR_VALUE)
            .map(square)
            .and_then(ok_if_positive)
            .or_else(err_to_other_err) # Err(OTHER_ERR_VALUE)
            .map(lambda x: x + 1)
            .expect_err("Should be other error")
    )
    assert res == OTHER_ERR_VALUE

