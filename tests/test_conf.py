import recoverpy
from os import environ


def test_conf_parsing():
    recoverpy.parse_configuration()

    assert recoverpy.SAVER._SAVE_PATH == "/tmp/"
    assert recoverpy.LOGGER._LOG_FILE_PATH == "/tmp/"


def test_terminal_fix():
    recoverpy.verify_terminal_conf()

    assert environ["TERM"] == "xterm-256color"
