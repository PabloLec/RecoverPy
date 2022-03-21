class NoSavePath(Exception):
    def __init__(self):
        super().__init__(
            "No path entered for saving in config file. Verify your 'config.yaml' file."
        )


class InvalidSavePath(Exception):
    def __init__(self):
        super().__init__(
            "Path entered for saving in config file is invalid. "
            "Verify your 'config.yaml' file."
        )


class InvalidLogPath(Exception):
    def __init__(self):
        super().__init__(
            "Path entered for logging in config file is invalid. "
            "Verify your 'config.yaml' file\n"
            'You can leave the location blank ( "" ) if you want to disable it.'
        )
