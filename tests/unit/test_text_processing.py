import pytest

from recoverpy.lib.text.text_processing import get_inode


def test_get_inode_parses_leading_number():
    assert get_inode("12345:some result") == 12345


def test_get_inode_rejects_line_without_inode():
    with pytest.raises(ValueError):
        get_inode("no inode prefix here")
