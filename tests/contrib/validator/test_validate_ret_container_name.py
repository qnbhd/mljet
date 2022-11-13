import re
from functools import lru_cache

import pytest
from hypothesis import (
    given,
    strategies as st,
)

from deployme.contrib.validator import validate_ret_container_name


# noinspection PyBroadException
def _docker_installed():
    try:
        import docker

        docker.from_env()
        return True
    except Exception:
        return False


@lru_cache(None)
def get_containers_list():
    import docker

    client = docker.from_env()
    return [cont.name for cont in client.containers.list()]


# integration test
@pytest.mark.skipif(
    not _docker_installed(), reason="Docker not installer or not running"
)
@given(
    name=st.from_regex(
        r"[a-zA-Z0-9][a-zA-Z0-9_.-]{10,}", fullmatch=True
    ).filter(lambda x: x not in get_containers_list())
)
def test_validate_ret_container_name(name):
    assert validate_ret_container_name(name) == name


@pytest.mark.skipif(
    not _docker_installed() or not get_containers_list(),
    reason="Docker not installer or not running or no containers",
)
@given(name=st.sampled_from(get_containers_list()))
def test_validate_ret_container_name_invalid(name):
    with pytest.raises(ValueError):
        validate_ret_container_name(name)


@given(
    st.text().filter(lambda x: not re.fullmatch(r"[a-zA-Z\d][a-zA-Z\d_.-]+", x))
)
def test_validate_ret_container_name_invalid_regex(name):
    with pytest.raises(ValueError):
        validate_ret_container_name(name)


@given(st.none())
def test_validate_ret_container_name_none(name):
    with pytest.raises(TypeError):
        validate_ret_container_name(name)
