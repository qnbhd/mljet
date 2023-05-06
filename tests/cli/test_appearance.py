import click
from click.testing import CliRunner

from mljet.cli.helpers import appearance


def test_appearance_no_args():
    @click.command("spam")
    @appearance()
    def spam():
        pass

    runner = CliRunner()
    result = runner.invoke(spam, ["--help"])
    assert "--colorized" not in result.output
    assert "Colorizes the output." not in result.output
    assert "--no-color" not in result.output
    assert "Prints the output without colorization." not in result.output

    assert "--plain" not in result.output
    assert "Prints the output without any formatting." not in result.output
    assert "--markdown" not in result.output
    assert "Prints in Markdown format." not in result.output
    assert "--json" not in result.output
    assert "Prints in JSON format." not in result.output


def test_appearance_colorization():
    @click.command("spam")
    @appearance(dest_printer="echo")
    def spam(echo):
        pass

    runner = CliRunner()
    result = runner.invoke(spam, ["--help"])
    assert "--colorized" in result.output
    assert "Colorizes the output." in result.output
    assert "--no-color" in result.output
    assert "Prints the output without colorization." in result.output

    result = runner.invoke(spam, ["echo=woo"])
    assert result.exit_code == 2


def test_appearance_formatting():
    @click.command("spam")
    @appearance(dest_formatting="echo")
    def spam(echo):
        pass

    runner = CliRunner()
    result = runner.invoke(spam, ["--help"])
    assert "--plain" in result.output
    assert "Prints the output without any formatting." in result.output
    assert "--markdown" in result.output
    assert "Prints in Markdown format." in result.output
    assert "--json" in result.output
    assert "Prints in JSON format." in result.output
