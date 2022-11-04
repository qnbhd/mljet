import pytest
from hypothesis import given
from hypothesis.strategies import (
    sampled_from,
    text,
)

from deployme.contrib.supported import Strategy
from deployme.contrib.validator import validate_ret_strategy


@given(strategy=sampled_from(Strategy))
def test_validate_ret_strategy_valid(strategy):
    """Ensures that valid strategy is returned."""
    assert validate_ret_strategy(strategy) == strategy


@given(strategy=sampled_from(list(Strategy.__members__.keys())))
def test_validate_ret_strategy_valid_str(strategy):
    """Ensures that method accepts strategy as string."""
    assert validate_ret_strategy(strategy) == strategy == Strategy(strategy)


@given(strategy=text().filter(lambda x: x not in Strategy.__members__.keys()))
def test_validate_ret_strategy_invalid(strategy):
    """Ensures that invalid strategy raises ValueError."""
    with pytest.raises(ValueError):
        validate_ret_strategy(strategy)
