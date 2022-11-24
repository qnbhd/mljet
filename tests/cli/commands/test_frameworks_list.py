from click.testing import CliRunner

from deployme.cli.commands.info.frameworks_list import frameworks_list
from deployme.contrib.supported import ModelType
from tests.cli.commands.testing import assert_support_appearance


def test_frameworks_list():
    runner = CliRunner()
    result = runner.invoke(frameworks_list)
    assert result.exit_code == 0
    assert result.output.strip() == ",".join(
        [m.replace("ModelType.", "") for m in ModelType]
    )
    assert_support_appearance(frameworks_list)
