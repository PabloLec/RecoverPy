class NoSavePath(Exception):
    """Raised when save path is not set in config file"""

    def __init__(self):
        super().__init__(
            "No path entered for saving in config file. Verify your 'config.yaml' file."
        )


class InvalidSavePath(Exception):
    """Raised when save path is invalid"""

    def __init__(self):
        super().__init__(
            "Path entered for saving in config file is invalid. Verify your 'config.yaml' file."
        )


class InvalidLogPath(Exception):
    """Raised when log path is invalid"""

    def __init__(self):
        super().__init__(
            "Path entered for logging in config file is invalid. Verify your 'config.yaml' file.\
                \nYou can leave the location blank ( \"\" ) if you want to disable it."
        )