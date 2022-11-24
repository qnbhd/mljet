from click.testing import CliRunner

from deployme.cli.commands.info.about import about


def test_about_command():
    runner = CliRunner()
    result = runner.invoke(about, [])
    assert result.exit_code == 0
    assert (
        "DeployMe - minimalistic ML-models auto deployment tool."
        in result.output
    )
    assert "Authors" in result.output
    assert "Github" in result.output
    assert "PyPI" in result.output
    assert "ReadTheDocs" in result.output
