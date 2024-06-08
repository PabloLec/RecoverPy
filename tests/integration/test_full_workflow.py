from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

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


@pytest.mark.asyncio(scope="class")
@pytest.mark.incremental
class TestFullWorkflow:
    @pytest_asyncio.fixture(scope="class")
    def session_patch(self, session_mocker):
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

    @pytest_asyncio.fixture(scope="class")
    async def pilot(self, session_patch):
        async with RecoverpyApp().run_test() as p:
            yield p

    async def test_init_app(self, pilot):
        assert pilot.app is not None
        for screen in pilot.app.screens:
            assert pilot.app.is_screen_installed(pilot.app.screens[screen])
        assert pilot.app.screen.name == "params"
        assert pilot.app.screen._partition_list is not None
        assert (
            len(pilot.app.screen._partition_list.list_items) == VISIBLE_PARTITION_COUNT
        )
        assert pilot.app.screen._start_search_button.disabled is True

    async def test_partition_list_default_state(self, pilot):
        filter_checkbox = pilot.app.query("Checkbox").only_one()
        assert filter_checkbox is not None
        assert filter_checkbox.value is True

        items = list(pilot.app.query("ListItem").results())
        assert len(items) == VISIBLE_PARTITION_COUNT

    async def test_partition_list_unfiltered(self, pilot):
        filter_checkbox = pilot.app.query("Checkbox").only_one()
        filter_checkbox.toggle()
        await pilot.pause()

        assert filter_checkbox.value is False
        await assert_with_timeout(
            lambda: len(list(pilot.app.query("ListItem").results()))
            == UNFILTERED_PARTITION_COUNT,
            UNFILTERED_PARTITION_COUNT,
            len(list(pilot.app.query("ListItem").results())),
        )

    async def test_partition_list_filtered(self, pilot):
        filter_checkbox = pilot.app.query("Checkbox").only_one()
        filter_checkbox.toggle()
        await pilot.pause()

        assert filter_checkbox.value is True
        await assert_with_timeout(
            lambda: len(list(pilot.app.query("ListItem").results()))
            == VISIBLE_PARTITION_COUNT,
            VISIBLE_PARTITION_COUNT,
            len(list(pilot.app.query("ListItem").results())),
        )

    async def test_input_search_params(self, pilot):
        await pilot.click("#search-input")
        await pilot.pause()

        for c in "TEST":
            await pilot.press(c)

        assert pilot.app.screen._search_input.value == "TEST"

        await pilot.click(f"#{TEST_PARTITION}")
        await pilot.pause()

        assert pilot.app.screen._partition_list.highlighted_child is not None
        assert pilot.app.screen._partition_list.highlighted_child.id == TEST_PARTITION
        assert pilot.app.screen._start_search_button.disabled is False

    async def test_start_search(self, pilot):
        await pilot.click("#start-search-button")
        await pilot.pause()

        assert pilot.app.screen.name == "search"
        assert hasattr(pilot.app.screen, "search_engine")
        assert pilot.app.screen.search_engine.search_params.search_string == "TEST"
        assert (
            pilot.app.screen.search_engine.search_params.partition
            == TEST_FULL_PARTITION
        )

    async def test_search_results(self, pilot):
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
            lambda: len(list(pilot.app.query("ListItem").results()))
            == GREP_RESULT_COUNT,
            GREP_RESULT_COUNT,
            len(list(pilot.app.query("ListItem").results())),
        )

    async def test_select_search_results(self, pilot):
        list_items = list(pilot.app.query("ListItem").results())

        for item in list_items:
            await pilot.click(f"#{item.id}")
            await pilot.pause()

            assert item.highlighted is True
            assert pilot.app.screen._get_selected_grep_result().list_item == item

    async def test_open_result(self, pilot):
        select_item = pilot.app.screen._grep_result_list.highlighted_child
        assert select_item is not None
        select_grep_result = pilot.app.screen._get_selected_grep_result()
        assert select_grep_result.list_item == select_item

        await pilot.click("#open-button")
        await pilot.pause()

        assert pilot.app.screen.name == "result"

        assert pilot.app.screen._partition == TEST_FULL_PARTITION
        assert pilot.app.screen._block_size == TEST_BLOCK_SIZE
        assert pilot.app.screen._inode == select_grep_result.inode

    async def test_result_content(self, pilot):
        await pilot.pause()

        assert (
            str(pilot.app.screen._inode)
            in pilot.app.screen._inode_label.renderable.plain
        )
        assert pilot.app.screen._block_count_label.renderable.plain.startswith("0 ")
        assert get_expected_block_content_text(
            pilot.app.screen._inode
        ) == get_block_content_text(pilot.app.screen._block_content)

    async def test_select_first_result(self, pilot):
        await pilot.click("#add-block-button")
        await pilot.pause()

        assert pilot.app.screen._block_count_label.renderable.plain.startswith("1 ")
        assert pilot.app.screen._save_button.disabled is False

        assert len(pilot.app.screen._saver._results) == 1
        await assert_current_result_is_selected_for_save(pilot)

        await pilot.click("#add-block-button")
        await pilot.pause()

        assert len(pilot.app.screen._saver._results) == 1
        add_expected_save_result(pilot)

    async def test_select_next_result(self, pilot):
        current_inode = pilot.app.screen._inode
        await pilot.click("#next-button")
        await pilot.pause()

        assert pilot.app.screen._inode != current_inode

        assert (
            str(pilot.app.screen._inode)
            in pilot.app.screen._inode_label.renderable.plain
        )

        assert get_expected_block_content_text(
            pilot.app.screen._inode
        ) == get_block_content_text(pilot.app.screen._block_content)

        await pilot.click("#add-block-button")
        await pilot.pause()

        assert pilot.app.screen._block_count_label.renderable.plain.startswith("2 ")

        assert len(pilot.app.screen._saver._results) == 2
        await assert_current_result_is_selected_for_save(pilot)

        await pilot.click("#add-block-button")
        assert len(pilot.app.screen._saver._results) == 2
        add_expected_save_result(pilot)

    async def test_select_previous_result(self, pilot):
        current_inode = pilot.app.screen._inode
        await pilot.click("#previous-button")
        await pilot.pause()

        assert pilot.app.screen._inode != current_inode

        current_inode = pilot.app.screen._inode
        await pilot.click("#previous-button")
        await pilot.pause()

        assert pilot.app.screen._inode != current_inode

        assert (
            str(pilot.app.screen._inode)
            in pilot.app.screen._inode_label.renderable.plain
        )
        assert get_expected_block_content_text(
            pilot.app.screen._inode
        ) == get_block_content_text(pilot.app.screen._block_content)

        await pilot.click("#add-block-button")
        await pilot.pause()

        assert pilot.app.screen._block_count_label.renderable.plain.startswith("3 ")

        assert len(pilot.app.screen._saver._results) == 3
        await assert_current_result_is_selected_for_save(pilot)

        await pilot.click("#add-block-button")
        await pilot.pause()

        assert len(pilot.app.screen._saver._results) == 3
        add_expected_save_result(pilot)

    async def test_start_save_process(self, pilot):
        await pilot.click("#save-button")
        await pilot.pause()

        assert pilot.app.screen.name == "save"

    async def test_edit_save_path(self, pilot, tmp_path: Path):
        await pilot.click("#edit-save-path-button")
        await pilot.pause()

        assert pilot.app.screen.name == "path_edit"

        tmp_tree_node = None
        for n in pilot.app.screen._directory_tree._tree_nodes.values():
            if "tmp" in n._label:
                tmp_tree_node = n
                break

        assert tmp_tree_node is not None
        pilot.app.screen._directory_tree.selected_dir = tmp_path

        await pilot.click("#confirm-button")
        await pilot.pause()

        assert pilot.app.screen.name == "save"
        assert pilot.app.screen._saver.save_path == tmp_path

    async def test_save_results(self, pilot):
        await pilot.click("#save-button")
        await pilot.pause()

        assert pilot.app.screen.name == "save-modal"

        await pilot.click("#ok-button")
        await pilot.pause()

        assert pilot.app.screen.name == "result"

    def check_saved_result(self, tmp_path: Path):
        dir_files = list(tmp_path.iterdir())
        assert len(dir_files) == 1
        assert dir_files[0].name.startswith("recoverpy-save-")

        with open(dir_files[0], "r") as f:
            result = f.read()
            assert result == get_expected_save_result()
