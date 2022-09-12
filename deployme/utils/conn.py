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

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def find_free_port():
    """
    Find a free port.

    Returns:
        Number of free port to use.

    """

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
