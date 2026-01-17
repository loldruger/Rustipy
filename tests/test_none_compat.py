from rustipy.option import Option, Some, NONE

def test_from_optional_with_value():
    val = 123
    opt = Option.from_optional(val)
    assert opt == Some(123)
    assert opt.is_some()

def test_from_optional_with_none():
    val = None
    opt = Option.from_optional(val)
    assert opt == NONE
    assert opt.is_none()

def test_unwrap_or_none_some():
    opt = Some("hello")
    assert opt.unwrap_or_none() == "hello"

def test_unwrap_or_none_nothing():
    opt = NONE
    assert opt.unwrap_or_none() is None

def test_round_trip():
    # value -> option -> value
    original = 42
    opt = Option.from_optional(original)
    result = opt.unwrap_or_none()
    assert result == original

    # none -> option -> none
    original_none = None
    opt_none = Option.from_optional(original_none)
    result_none = opt_none.unwrap_or_none()
    assert result_none is None
