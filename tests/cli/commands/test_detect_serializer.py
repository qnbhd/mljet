from unittest.mock import patch

from click.testing import CliRunner

from mljet.cli.commands.tools.detect_serializer import detect_serializer


def test_detect_serializer():
    runner = CliRunner()

    with patch(
        "mljet.cli.commands" ".tools.detect_serializer.detect_model_serializer",
        return_value="pickle",
    ) as mock:
        result = runner.invoke(detect_serializer, [__file__])
        assert result.exit_code == 0
        assert mock.call_count == 1
        assert result.output.strip() == "pickle"
