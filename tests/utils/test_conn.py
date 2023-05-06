import socket
from contextlib import closing
from unittest.mock import patch

from mljet.utils.conn import (
    find_free_port,
    is_port_in_use,
)


def test_find_free_port():
    free_port = find_free_port()
    assert isinstance(free_port, int)


def test_port_in_use():
    free_port = find_free_port()
    assert not is_port_in_use(free_port)
    # check if port is in use
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        assert is_port_in_use(port)
