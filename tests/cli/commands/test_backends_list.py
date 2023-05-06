from click.testing import CliRunner

from mljet.cli.commands.info.backends_list import backends_list
from mljet.cookie.templates.backends.dispatcher import SUPPORTED_BACKENDS
from tests.cli.commands.testing import assert_support_appearance


def test_backends_list():
    runner = CliRunner()
    result = runner.invoke(backends_list)
    assert result.exit_code == 0
    assert result.output.strip() == ",".join(SUPPORTED_BACKENDS.keys())

    assert_support_appearance(backends_list)
