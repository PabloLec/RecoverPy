from recoverpy.ui.screens.screen_save import SaveScreen


def test_check_action_disables_save_without_saver() -> None:
    screen = SaveScreen()

    assert screen.check_action("save", ()) is None
