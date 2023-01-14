from logging import getLogger

from recoverpy.ui.app import RecoverpyApp

getLogger(__name__)


def main() -> None:
    RecoverpyApp().run()


if __name__ == "__main__":
    main()
