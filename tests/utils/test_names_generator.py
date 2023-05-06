import random

from mljet.utils.names_generator import get_random_name


def test_get_random_name():
    random.seed(0)
    assert get_random_name() == "hopeful_sanderson"
    assert get_random_name() == "interesting_banach"
    # teardown
    random.seed(None)
