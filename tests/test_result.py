import pytest

from src.rustipy.result import Ok, Err, Result, is_ok, is_err
from src.rustipy.option import Some, NOTHING, Option

# --- Test Data ---
OK_VALUE = 100
ERR_VALUE = "Error occurred"
OTHER_OK_VALUE = 200
OTHER_ERR_VALUE = "Another error"
DEFAULT_VALUE = 0
DEFAULT_ERR = "Default Error"

# --- Helper Functions ---
def square(x: int) -> int:
    return x * x

def stringify(x: int) -> str:
    return str(x)

def len_str(s: str) -> int:
    return len(s)

def check_positive(x: int) -> bool:
    return x > 0

def check_contains_error(s: str) -> bool:
    return "error" in s.lower()

def ok_if_positive(x: int) -> Result[int, str]:
    if x > 0:
        return Ok(x)
    else:
        return Err("Not positive")

def err_if_negative(x: int) -> Result[int, str]:
    if x < 0:
        return Err("Is negative")
    else:
        return Ok(x)

def err_to_str(e: str) -> str:
    return f"Error: {e}"

def err_to_default_ok(e: str) -> Result[int, str]:
    return Ok(DEFAULT_VALUE)

def err_to_other_err(e: str) -> Result[int, str]:
    return Err(OTHER_ERR_VALUE)

def ok_to_str(x: int) -> str:
    return f"Value: {x}"

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
    assert ok_res.map_or(DEFAULT_VALUE, stringify) == str(OK_VALUE)
    assert err_res.map_or(DEFAULT_VALUE, stringify) == DEFAULT_VALUE

def test_map_or_else():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.map_or_else(len_str, stringify) == str(OK_VALUE)
    assert err_res.map_or_else(len_str, stringify) == len(ERR_VALUE)

def test_map_or_default():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    # Assuming default for str is ""
    with pytest.raises(NotImplementedError):
        err_res.map_or_default(stringify) # Default for U (str) is hard

    # Test Ok case (requires knowing default of U)
    # We can't reliably test Ok case without knowing U's default
    # assert ok_res.map_or_default(stringify) == str(OK_VALUE) # This works if U=str

    # Let's test with a type whose default is known (e.g., int -> 0)
    ok_int_res: Result[int, str] = Ok(5)
    err_int_res: Result[int, str] = Err("error")
    assert ok_int_res.map_or_default(square) == 25
    with pytest.raises(NotImplementedError):
         err_int_res.map_or_default(square) # Default for U (int) is needed


# --- Inspection ---
def test_inspect():
    inspected_ok = None
    def inspect_ok_fn(x: int):
        nonlocal inspected_ok
        inspected_ok = x

    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert ok_res.inspect(inspect_ok_fn) is ok_res # Returns self
    assert inspected_ok == OK_VALUE

    inspected_ok = None # Reset
    assert err_res.inspect(inspect_ok_fn) is err_res # Returns self
    assert inspected_ok is None # Function not called for Err

def test_inspect_err():
    inspected_err = None
    def inspect_err_fn(e: str):
        nonlocal inspected_err
        inspected_err = e

    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert ok_res.inspect_err(inspect_err_fn) is ok_res # Returns self
    assert inspected_err is None # Function not called for Ok

    inspected_err = None # Reset
    assert err_res.inspect_err(inspect_err_fn) is err_res # Returns self
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

    # Err case raises NotImplementedError
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
    err_neg: Result[int, str] = Err("negative") # Example error for err_to_other_err

    assert ok_res.or_else(err_to_default_ok) == Ok(OK_VALUE)
    assert ok_res.or_else(err_to_other_err) == Ok(OK_VALUE)

    assert err_orig.or_else(err_to_default_ok) == Ok(DEFAULT_VALUE)
    assert err_orig.or_else(err_to_other_err) == Err(OTHER_ERR_VALUE)

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
    ok2: Result[int, str] = Ok(OTHER_OK_VALUE) # Note: T must match for Ok case
    err1: Result[int, str] = Err(ERR_VALUE)
    err2: Result[int, str] = Err(OTHER_ERR_VALUE) # Note: F can differ

    ok3_diff_f: Result[int, int] = Ok(300)
    err3_diff_f: Result[int, int] = Err(999)


    assert ok1.or_(ok2) == Ok(OK_VALUE)
    assert ok1.or_(err3_diff_f) == Ok(OK_VALUE) # F changes, but Ok1 returned
    assert err1.or_(ok2) == Ok(OTHER_OK_VALUE)
    assert err1.or_(err3_diff_f) == Err(999) # F changes to int

# --- Iteration ---
def test_iter():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    ok_list = list(ok_res.iter())
    err_list = list(err_res.iter())

    assert ok_list == [OK_VALUE]
    assert err_list == []

def test_iter_mut():
    # Note: Python's iterators don't inherently track mutability like Rust's.
    # This test demonstrates yielding the value, which can be mutated if mutable.
    mutable_val = [1, 2]
    ok_res: Result[list[int], str] = Ok(mutable_val)
    err_res: Result[list[int], str] = Err(ERR_VALUE)

    ok_iter = ok_res.iter_mut()
    try:
        val_ref = next(ok_iter)
        assert val_ref is mutable_val # Should be the same object
        val_ref.append(3)
    except StopIteration:
        pytest.fail("Iterator for Ok should yield one value")

    assert mutable_val == [1, 2, 3] # Original value is mutated
    assert ok_res.unwrap() == [1, 2, 3] # The result now holds the mutated value

    err_iter = err_res.iter_mut()
    with pytest.raises(StopIteration):
        next(err_iter) # Iterator for Err should be empty

# --- Flattening and Transposing ---
def test_flatten():
    ok_ok: Result[Result[int, str], str] = Ok(Ok(OK_VALUE))
    ok_err: Result[Result[int, str], str] = Ok(Err(ERR_VALUE))
    err_outer: Result[Result[int, str], str] = Err(OTHER_ERR_VALUE)
    ok_not_result: Result[int, str] = Ok(123) # Non-nested Result

    assert ok_ok.flatten() == Ok(OK_VALUE)
    assert ok_err.flatten() == Err(ERR_VALUE)
    assert err_outer.flatten() == Err(OTHER_ERR_VALUE)

    with pytest.raises(TypeError):
        ok_not_result.flatten() # Cannot flatten Ok containing non-Result

def test_transpose():
    ok_some: Result[Option[int], str] = Ok(Some(OK_VALUE))
    ok_nothing: Result[Option[int], str] = Ok(NOTHING)
    err_res: Result[Option[int], str] = Err(ERR_VALUE)
    ok_not_option: Result[int, str] = Ok(123) # Non-Option value

    assert ok_some.transpose() == Some(Ok(OK_VALUE))
    assert ok_nothing.transpose() == NOTHING
    assert err_res.transpose() == Some(Err(ERR_VALUE))

    with pytest.raises(TypeError):
        ok_not_option.transpose() # Cannot transpose Ok containing non-Option

# --- Consuming Operations (Conceptual) ---
def test_into_ok():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert ok_res.into_ok() == OK_VALUE
    # Note: In Python, the original object isn't truly consumed/invalidated
    assert ok_res.is_ok() # Still usable

    with pytest.raises(ValueError, match=f"Called into_ok on an Err value: '{ERR_VALUE}'"):
        err_res.into_ok()

def test_into_err():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert err_res.into_err() == ERR_VALUE
    # Note: In Python, the original object isn't truly consumed/invalidated
    assert err_res.is_err() # Still usable

    with pytest.raises(ValueError, match=f"Called into_err on an Ok value: {OK_VALUE}"):
        ok_res.into_err()

# --- Copying and Cloning ---
def test_cloned():
    original_list = [1, 2]
    ok_res: Result[list[int], str] = Ok(original_list)
    err_res: Result[int, list[int]] = Err(original_list)

    cloned_ok = ok_res.cloned()
    assert cloned_ok == ok_res
    assert cloned_ok.unwrap() is not original_list # Deep copy
    cloned_ok.unwrap().append(3)
    assert original_list == [1, 2] # Original unchanged

    cloned_err = err_res.cloned()
    assert cloned_err == err_res
    assert cloned_err.unwrap_err() is not original_list # Deep copy
    cloned_err.unwrap_err().append(3)
    assert original_list == [1, 2] # Original unchanged

def test_copied():
    original_list = [1, 2]
    ok_res: Result[list[int], str] = Ok(original_list)
    err_res: Result[int, list[int]] = Err(original_list)

    copied_ok = ok_res.copied()
    assert copied_ok == ok_res
    assert copied_ok.unwrap() is not original_list # Shallow copy (new outer list)
    # However, elements might be shared if mutable
    # assert copied_ok.unwrap()[0] is original_list[0] # If elements were objects

    copied_ok.unwrap().append(3)
    assert original_list == [1, 2] # Original unchanged by appending to copy

    copied_err = err_res.copied()
    assert copied_err == err_res
    assert copied_err.unwrap_err() is not original_list # Shallow copy
    copied_err.unwrap_err().append(3)
    assert original_list == [1, 2] # Original unchanged

# --- References (Conceptual in Python) ---
def test_as_ref():
    # In Python, these likely just return self. Test they don't error.
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.as_ref() is ok_res
    assert err_res.as_ref() is err_res

def test_as_mut():
    # In Python, these likely just return self. Test they don't error.
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    assert ok_res.as_mut() is ok_res
    assert err_res.as_mut() is err_res

# --- Containment Checks ---
def test_contains():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    ok_other: Result[int, str] = Ok(OTHER_OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)

    assert ok_res.contains(OK_VALUE) is True
    assert ok_res.contains(OTHER_OK_VALUE) is False
    assert ok_other.contains(OK_VALUE) is False
    assert err_res.contains(OK_VALUE) is False

def test_contains_err():
    ok_res: Result[int, str] = Ok(OK_VALUE)
    err_res: Result[int, str] = Err(ERR_VALUE)
    err_other: Result[int, str] = Err(OTHER_ERR_VALUE)

    assert ok_res.contains_err(ERR_VALUE) is False
    assert err_res.contains_err(ERR_VALUE) is True
    assert err_res.contains_err(OTHER_ERR_VALUE) is False
    assert err_other.contains_err(ERR_VALUE) is False

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

def test_repr():
    assert repr(Ok(10)) == "Ok(10)"
    assert repr(Err("error")) == "Err('error')"
    assert repr(Ok("hello")) == "Ok('hello')"
    assert repr(Err(None)) == "Err(None)"
    assert repr(Ok([1, 2])) == "Ok([1, 2])"

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

