from recoverpy.lib.logger import Logger


def get_log_file_content():
    log_file_path = Logger()._logger.handlers[0].baseFilename
    with open(log_file_path, "r") as f:
        return f.read().strip()


def test_log_disabled():
    Logger().log_enabled = False
    Logger().write("debug", "debug")

    assert "debug" not in get_log_file_content()


def test_debug():
    Logger().log_enabled = True
    Logger().write("debug", "debug")

    assert "debug" in get_log_file_content()


def test_info():
    Logger().write("info", "info")

    assert "info" in get_log_file_content()


def test_warning():
    Logger().write("warning", "warning")

    assert "warning" in get_log_file_content()


def test_error():
    Logger().write("error", "error")

    assert "error" in get_log_file_content()


def test_critical():
    Logger().write("critical", "critical")

    assert "critical" in get_log_file_content()
