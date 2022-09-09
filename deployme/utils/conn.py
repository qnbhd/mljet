import socket


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
