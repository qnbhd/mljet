import logging

import pytest

from mljet.utils.logging_ import RichEmojiFilteredHandler


@pytest.mark.parametrize(
    "enable_emoji",
    [
        True,
        False,
    ],
)
def test_filter_emoji(enable_emoji):
    handler = RichEmojiFilteredHandler(enable_emoji=enable_emoji)
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test",
        lineno=1,
        msg="test 🚀",
        args=None,
        exc_info=None,
    )
    formatted = handler.format(record)
    assert "🚀" in formatted if enable_emoji else "🚀" not in formatted
