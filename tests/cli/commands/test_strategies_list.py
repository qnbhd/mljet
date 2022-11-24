from click.testing import CliRunner

from deployme.cli.commands.info.strategies_list import strategies_list
from deployme.contrib.supported import Strategy
from tests.cli.commands.testing import assert_support_appearance


def test_frameworks_list():
    runner = CliRunner()
    result = runner.invoke(strategies_list)
    assert result.exit_code == 0
    assert result.output.strip() == ",".join(
        [m.replace("Strategy.", "") for m in Strategy]
    )
    assert_support_appearance(strategies_list)
