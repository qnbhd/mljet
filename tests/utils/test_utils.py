from mljet.utils.utils import drop_unnecessary_kwargs


def test_drop_unnecessary_kwargs():
    """Test drop_unnecessary_kwargs."""

    def test_func(a, b, c):
        pass

    kwargs = {"a": 1, "b": 2, "c": 3, "d": 4}
    assert drop_unnecessary_kwargs(test_func, kwargs) == {
        "a": 1,
        "b": 2,
        "c": 3,
    }
