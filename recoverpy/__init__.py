from logging import getLogger

from ui.app import RecoverPyApp

getLogger(__name__)

def main() -> None:
    RecoverPyApp().run()

if __name__ == "__main__":
    main()