from datetime import datetime

from recoverpy.utils.logger import LOGGER


class Saver:
    """Encapsulates all result saving related methods."""

    def __init__(self):
        self.save_path: str = None
        self.last_saved_file: str = None

    def save_result_string(self, result: str):
        time_format: str = datetime.now().strftime("recoverpy-save-%Y-%m-%d-%H%M%S")
        file_name: str = f"{self.save_path}{time_format}"

        self.write_to_file(file_name=file_name, content=result)

    def save_result_dict(self, results: dict):
        ordered_blocks: list = [results[num] for num in sorted(results.keys())]
        final_output: str = "\n".join(ordered_blocks)

        self.save_result_string(final_output)

    def write_to_file(self, file_name: str, content: str):
        with open(file_name, "w") as save_file:
            save_file.write(content)

        self.last_saved_file = file_name

        LOGGER.write("info", f"Output saved in file {file_name}")


SAVER: Saver = Saver()
