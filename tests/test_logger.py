from recoverpy.utils.logger import LOGGER


def get_log_file_content():
    log_file_path = LOGGER._logger.handlers[0].baseFilename
    with open(log_file_path, "r") as f:
        return f.read().strip()


def test_log_disabled():
    LOGGER.log_enabled = False
    LOGGER.write("debug", "debug")

    assert "debug" not in get_log_file_content()


def test_debug():
    LOGGER.log_enabled = True
    LOGGER.write("debug", "debug")

    assert "debug" in get_log_file_content()


def test_info():
    LOGGER.write("info", "info")

    assert "info" in get_log_file_content()


def test_warning():
    LOGGER.write("warning", "warning")

    assert "warning" in get_log_file_content()


def test_error():
    LOGGER.write("error", "error")

    assert "error" in get_log_file_content()


def test_critical():
    LOGGER.write("critical", "critical")

    assert "critical" in get_log_file_content()
