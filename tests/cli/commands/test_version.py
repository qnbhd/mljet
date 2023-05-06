from click.testing import CliRunner

from mljet import __version__
from mljet.cli.commands.info.version import version
from mljet.contrib.supported import Strategy
from tests.cli.commands.testing import assert_support_appearance


def test_version():
    runner = CliRunner()
    result = runner.invoke(version)
    assert result.exit_code == 0
    assert result.output.strip() == __version__
    assert_support_appearance(version)
