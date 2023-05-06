from mljet.utils.logging_ import init


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    init(verbose=True)
