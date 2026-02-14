from recoverpy.ui.screens.screen_params import ParamsScreen


def test_check_action_disables_start_without_input() -> None:
    screen = ParamsScreen()
    screen._search_input = type("FakeInput", (), {"value": ""})()  # type: ignore[assignment]
    screen._partition_list = None

    assert screen.check_action("start_search", ()) is None
