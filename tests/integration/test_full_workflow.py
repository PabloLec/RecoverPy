from pathlib import Path
from unittest.mock import MagicMock

import pytest
from textual.widgets import DirectoryTree

from recoverpy import RecoverpyApp
from tests.conftest import TEST_BLOCK_SIZE
from tests.fixtures.mock_grep_process import GREP_RESULT_COUNT
from tests.fixtures.mock_lsblk_output import (
    UNFILTERED_PARTITION_COUNT,
    VISIBLE_PARTITION_COUNT,
)
from tests.integration.helper import (
    TEST_FULL_PARTITION,
    TEST_PARTITION,
    add_expected_save_result,
    assert_current_result_is_selected_for_save,
    assert_with_timeout,
    get_block_content_text,
    get_expected_block_content_text,
    get_expected_save_result,
)


@pytest.mark.asyncio
async def test_full_workflow(session_mocker, tmp_path: Path):
    # Apply patches
    session_mocker.patch(
        "recoverpy.lib.env_check._is_user_root",
        MagicMock(return_value=True),
    )
    session_mocker.patch(
        "recoverpy.lib.env_check._are_system_dependencies_installed",
        MagicMock(return_value=True),
    )
    session_mocker.patch(
        "recoverpy.lib.env_check._is_linux",
        MagicMock(return_value=True),
    )

    # Launch the application
    async with RecoverpyApp().run_test() as pilot:
        # Test initialization of the app
        assert pilot.app is not None
        for screen in pilot.app.screens:
            assert pilot.app.is_screen_installed(pilot.app.screens[screen])
        assert pilot.app.screen.name == "params"
        assert pilot.app.focused is not None
        assert pilot.app.focused.id == "search-input"

        await pilot.pause()
        assert pilot.app.screen._partition_list is not None
        assert (
            len(pilot.app.screen._partition_list.list_items) == VISIBLE_PARTITION_COUNT
        )
        assert pilot.app.screen._start_search_button.disabled is True

        # Test partition list default state
        filter_checkbox = pilot.app.screen.query("Checkbox").only_one()
        assert filter_checkbox is not None
        assert filter_checkbox.value is True

        items = list(pilot.app.screen.query("ListItem").results())
        assert len(items) == VISIBLE_PARTITION_COUNT

        # Test partition list unfiltered
        filter_checkbox.toggle()
        await pilot.pause()

        assert filter_checkbox.value is False
        await assert_with_timeout(
            lambda: len(list(pilot.app.screen.query("ListItem").results()))
            == UNFILTERED_PARTITION_COUNT,
            UNFILTERED_PARTITION_COUNT,
            len(list(pilot.app.screen.query("ListItem").results())),
        )

        # Test partition list filtered
        filter_checkbox.toggle()
        await pilot.pause()

        assert filter_checkbox.value is True
        await assert_with_timeout(
            lambda: len(list(pilot.app.screen.query("ListItem").results()))
            == VISIBLE_PARTITION_COUNT,
            VISIBLE_PARTITION_COUNT,
            len(list(pilot.app.screen.query("ListItem").results())),
        )

        # Test input search parameters
        for c in "TEST":
            await pilot.press(c)

        assert pilot.app.screen._search_input.value == "TEST"

        await pilot.click(f"#{TEST_PARTITION}")
        await pilot.pause()

        assert pilot.app.screen._partition_list.highlighted_child is not None
        assert pilot.app.screen._partition_list.highlighted_child.id == TEST_PARTITION
        assert pilot.app.screen._start_search_button.disabled is False

        # Test start search
        await pilot.press("enter")
        await pilot.pause()

        assert pilot.app.screen.name == "search"
        assert hasattr(pilot.app.screen, "search_engine")
        assert pilot.app.screen.search_engine.search_params.search_string == "TEST"
        assert (
            pilot.app.screen.search_engine.search_params.partition
            == TEST_FULL_PARTITION
        )

        # Test search results
        await assert_with_timeout(
            lambda: int(pilot.app.screen.search_engine.search_progress.progress_percent)
            == 100,
            100.0,
            pilot.app.screen.search_engine.search_progress.progress_percent,
        )
        await assert_with_timeout(
            lambda: pilot.app.screen.search_engine.search_progress.result_count
            == GREP_RESULT_COUNT,
            GREP_RESULT_COUNT,
            pilot.app.screen.search_engine.search_progress.result_count,
        )
        await assert_with_timeout(
            lambda: len(pilot.app.screen._grep_result_list.grep_results)
            == GREP_RESULT_COUNT,
            GREP_RESULT_COUNT,
            len(pilot.app.screen._grep_result_list.grep_results),
        )
        await assert_with_timeout(
            lambda: len(list(pilot.app.screen.query("ListItem").results()))
            == GREP_RESULT_COUNT,
            GREP_RESULT_COUNT,
            len(list(pilot.app.screen.query("ListItem").results())),
        )
        await assert_with_timeout(
            lambda: str(pilot.app.screen._search_status_label.content) == "Completed",
            "Completed",
            str(pilot.app.screen._search_status_label.content),
        )

        # Test select search results
        list_items = list(pilot.app.screen.query("ListItem").results())

        for item in list_items:
            await pilot.click(f"#{item.id}")
            await pilot.pause()

            assert item.highlighted is True
            assert pilot.app.screen._get_selected_grep_result().list_item == item

        # Test open result
        select_item = pilot.app.screen._grep_result_list.highlighted_child
        assert select_item is not None
        select_grep_result = pilot.app.screen._get_selected_grep_result()
        assert select_grep_result.list_item == select_item

        await pilot.press("o")
        await pilot.pause()

        assert pilot.app.screen.name == "result"

        assert pilot.app.screen._partition == TEST_FULL_PARTITION
        assert pilot.app.screen._block_size == TEST_BLOCK_SIZE
        assert pilot.app.screen._inode == select_grep_result.inode

        # Test result content
        await pilot.pause()

        assert str(pilot.app.screen._inode) in str(
            pilot.app.screen._inode_label.content
        )
        assert str(pilot.app.screen._block_count_label.content).startswith("0 ")
        assert get_expected_block_content_text(
            pilot.app.screen._inode
        ) == get_block_content_text(pilot.app.screen._block_content)

        # Test select first result
        await pilot.click("#add-block-button")
        await pilot.pause()

        assert str(pilot.app.screen._block_count_label.content).startswith("1 ")
        assert pilot.app.screen._save_button.disabled is False

        assert len(pilot.app.screen._saver._results) == 1
        await assert_current_result_is_selected_for_save(pilot)

        await pilot.click("#add-block-button")
        await pilot.pause()

        assert len(pilot.app.screen._saver._results) == 1
        add_expected_save_result(pilot)

        # Test select next result
        current_inode = pilot.app.screen._inode
        await pilot.press("right")
        await pilot.pause()

        assert pilot.app.screen._inode != current_inode

        assert str(pilot.app.screen._inode) in str(
            pilot.app.screen._inode_label.content
        )

        assert get_expected_block_content_text(
            pilot.app.screen._inode
        ) == get_block_content_text(pilot.app.screen._block_content)

        await pilot.click("#add-block-button")
        await pilot.pause()

        assert str(pilot.app.screen._block_count_label.content).startswith("2 ")

        assert len(pilot.app.screen._saver._results) == 2
        await assert_current_result_is_selected_for_save(pilot)

        await pilot.click("#add-block-button")
        await pilot.pause()

        assert len(pilot.app.screen._saver._results) == 2
        add_expected_save_result(pilot)

        # Test select previous result
        previous_button = pilot.app.screen.query("#previous-button").only_one()
        current_inode = pilot.app.screen._inode
        await pilot.press("left")
        await pilot.pause()

        assert pilot.app.screen._inode != current_inode

        current_inode = pilot.app.screen._inode

        await assert_with_timeout(
            lambda: not previous_button.has_class("-active"),
            False,
            not previous_button.has_class("-active"),
        )

        await pilot.press("left")
        await pilot.pause()

        assert pilot.app.screen._inode != current_inode

        assert str(pilot.app.screen._inode) in str(
            pilot.app.screen._inode_label.content
        )
        assert get_expected_block_content_text(
            pilot.app.screen._inode
        ) == get_block_content_text(pilot.app.screen._block_content)

        await pilot.click("#add-block-button")
        await pilot.pause()

        assert str(pilot.app.screen._block_count_label.content).startswith("3 ")

        assert len(pilot.app.screen._saver._results) == 3
        await assert_current_result_is_selected_for_save(pilot)

        await pilot.click("#add-block-button")
        await pilot.pause()

        assert len(pilot.app.screen._saver._results) == 3
        add_expected_save_result(pilot)

        # Test start save process
        await pilot.click("#save-button")
        await pilot.pause()

        assert pilot.app.screen.name == "save"
        assert pilot.app.focused is not None
        assert pilot.app.focused.id == "edit-save-path-button"

        # Test edit save path
        await pilot.press("e")
        await pilot.pause()

        assert pilot.app.screen.name == "path_edit"

        assert isinstance(pilot.app.screen._directory_tree, DirectoryTree)
        pilot.app.screen._selected_dir = str(tmp_path)

        await pilot.press("enter")
        await pilot.pause()

        assert pilot.app.screen.name == "save"
        assert pilot.app.screen._saver.save_path == tmp_path

        # Test save results
        await pilot.press("s")
        await pilot.pause()

        assert pilot.app.screen.name == "save-modal"

        await pilot.click("#ok-button")
        await pilot.pause()

        assert pilot.app.screen.name == "result"

        # Check saved result
        dir_files = list(tmp_path.iterdir())
        assert len(dir_files) == 1
        assert dir_files[0].name.startswith("recoverpy-save-")

        with open(dir_files[0], "r") as f:
            result = f.read()
            assert result == get_expected_save_result()
