from click.testing import CliRunner


def assert_support_appearance(click_command):
    runner = CliRunner()
    with_json = runner.invoke(click_command, ["--json"])
    assert with_json.exit_code == 0
    with_plain = runner.invoke(click_command, ["--plain"])
    assert with_plain.exit_code == 0
    with_markdown = runner.invoke(click_command, ["--markdown"])
    assert with_markdown.exit_code == 0
