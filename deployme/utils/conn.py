"""Helper functions for connecting across the network."""

import socket
from contextlib import closing


def is_port_in_use(port: int) -> bool:
    """
    Check if port is in use.

    Args:
        port: port to check

    Returns:
        True if port is in use, False otherwise
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0


def find_free_port() -> int:
    """
    Find a free port.

    Returns:
        Number of free port to use.

    """

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]
