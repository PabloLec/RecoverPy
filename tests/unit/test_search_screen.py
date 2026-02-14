from recoverpy.ui.screens.screen_search import SearchScreen


def test_check_action_disables_open_when_button_disabled() -> None:
    screen = SearchScreen()
    screen._open_button = type("FakeButton", (), {"disabled": True})()  # type: ignore[assignment]

    assert screen.check_action("open_result", ()) is None
