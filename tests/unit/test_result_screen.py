from recoverpy.ui.screens.screen_result import ResultScreen


def test_check_action_disables_previous_at_inode_zero() -> None:
    screen = ResultScreen()
    screen._inode = 0

    assert screen.check_action("previous", ()) is None


def test_check_action_disables_save_when_button_disabled() -> None:
    screen = ResultScreen()
    screen._save_button.disabled = True

    assert screen.check_action("save", ()) is None


def test_check_action_disables_add_block_without_content() -> None:
    screen = ResultScreen()
    screen._raw_block_content = None

    assert screen.check_action("add_block", ()) is None
