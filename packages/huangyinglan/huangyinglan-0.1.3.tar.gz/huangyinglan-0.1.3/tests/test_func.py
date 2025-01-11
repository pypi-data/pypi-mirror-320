from ..src.mylove.mfunc import myfunc

def test_func():
    result = myfunc()
    expect = "ok"

    assert result == expect
