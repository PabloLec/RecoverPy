import pytest
from textual.pilot import Pilot

from tests.conftest import TEST_BLOCK_SIZE
from tests.fixtures.mock_grep_process import GREP_RESULT_COUNT
from tests.fixtures.mock_lsblk_output import VISIBLE_PARTITION_COUNT
from tests.integration.helper import (
    TEST_FULL_PARTITION,
    TEST_PARTITION,
    assert_current_result_is_selected_for_save,
    assert_with_timeout,
    get_block_content_text,
    get_expected_block_content_text,
)


@pytest.mark.asyncio
async def test_init_app(pilot):
    async with pilot as p:
        await init_app(p)
        await input_search_params(p)
        await start_search(p)
        await verify_search_results(p)
        await select_search_results(p)
        await open_result(p)
        await verify_result(p)
        await select_first_result(p)
        await select_next_result(p)
        await select_previous_result(p)
        await start_save_process(p)
        await edit_save_path(p)


async def init_app(p: Pilot):
    assert p.app is not None
    for screen in p.app.screens:
        assert p.app.is_screen_installed(p.app.screens[screen])
    assert p.app.screen.name == "params"
    assert p.app.screen._partition_list is not None
    assert len(p.app.screen._partition_list.list_items) == VISIBLE_PARTITION_COUNT
    assert p.app.screen._start_search_button.disabled is True


async def input_search_params(p: Pilot):
    await p.click("#search-input")
    for c in "TEST":
        await p.press(c)

    assert p.app.screen._search_input.value == "TEST"

    await p.click(f"#{TEST_PARTITION}")

    assert p.app.screen._partition_list.highlighted_child is not None
    assert p.app.screen._partition_list.highlighted_child.id == TEST_PARTITION
    assert p.app.screen._start_search_button.disabled is False


async def start_search(p: Pilot):
    await p.click("#start-search-button")

    assert p.app.screen.name == "search"
    assert p.app.screen.search_engine.search_params.search_string == "TEST"
    assert p.app.screen.search_engine.search_params.partition == TEST_FULL_PARTITION


async def verify_search_results(p: Pilot):
    await assert_with_timeout(
        lambda: p.app.screen.search_engine.search_progress.progress_percent == 100.0
    )
    await assert_with_timeout(
        lambda: p.app.screen.search_engine.search_progress.result_count
        == GREP_RESULT_COUNT
    )
    await assert_with_timeout(
        lambda: len(p.app.screen._grep_result_list.grep_results) == GREP_RESULT_COUNT
    )
    await assert_with_timeout(
        lambda: len(list(p.app.query("ListItem").results())) == GREP_RESULT_COUNT
    )


async def select_search_results(p: Pilot):
    list_items = list(p.app.query("ListItem").results())

    for item in list_items:
        await p.click(f"#{item.id}")
        assert item.highlighted is True
        await assert_with_timeout(
            lambda: p.app.screen._get_selected_grep_result().list_item == item
        )


async def open_result(p: Pilot):
    select_item = p.app.screen._grep_result_list.highlighted_child
    assert select_item is not None
    select_grep_result = p.app.screen._get_selected_grep_result()
    assert select_grep_result.list_item == select_item

    await p.click("#open-button")

    assert p.app.screen.name == "result"

    await assert_with_timeout(lambda: p.app.screen._partition == TEST_FULL_PARTITION)
    await assert_with_timeout(lambda: p.app.screen._block_size == TEST_BLOCK_SIZE)
    await assert_with_timeout(lambda: p.app.screen._inode == select_grep_result.inode)


async def verify_result(p: Pilot):
    await assert_with_timeout(
        lambda: str(p.app.screen._inode) in p.app.screen._inode_label.renderable.plain
    )
    assert p.app.screen._block_count_label.renderable.plain.startswith("0 ")

    assert get_expected_block_content_text(
        p.app.screen._inode
    ) == get_block_content_text(p.app.screen._block_content)


async def select_first_result(p: Pilot):
    await p.click(f"#add-block-button")

    assert p.app.screen._block_count_label.renderable.plain.startswith("1 ")
    assert p.app.screen._save_button.disabled is False

    assert len(p.app.screen._saver._results) == 1
    await assert_current_result_is_selected_for_save(p)

    await p.click(f"#add-block-button")
    assert len(p.app.screen._saver._results) == 1


async def select_next_result(p: Pilot):
    current_inode = p.app.screen._inode
    await p.click(f"#next-button")
    assert p.app.screen._inode != current_inode

    await assert_with_timeout(
        lambda: str(p.app.screen._inode) in p.app.screen._inode_label.renderable.plain
    )
    assert get_expected_block_content_text(
        p.app.screen._inode
    ) == get_block_content_text(p.app.screen._block_content)

    await p.click(f"#add-block-button")

    assert p.app.screen._block_count_label.renderable.plain.startswith("2 ")

    assert len(p.app.screen._saver._results) == 2
    await assert_current_result_is_selected_for_save(p)

    await p.click(f"#add-block-button")
    assert len(p.app.screen._saver._results) == 2


async def select_previous_result(p: Pilot):
    current_inode = p.app.screen._inode
    await p.click(f"#previous-button")
    assert p.app.screen._inode != current_inode

    current_inode = p.app.screen._inode
    await p.click(f"#previous-button")
    assert p.app.screen._inode != current_inode

    await assert_with_timeout(
        lambda: str(p.app.screen._inode) in p.app.screen._inode_label.renderable.plain
    )
    assert get_expected_block_content_text(
        p.app.screen._inode
    ) == get_block_content_text(p.app.screen._block_content)

    await p.click(f"#add-block-button")

    assert p.app.screen._block_count_label.renderable.plain.startswith("3 ")

    assert len(p.app.screen._saver._results) == 3
    await assert_current_result_is_selected_for_save(p)

    await p.click(f"#add-block-button")
    assert len(p.app.screen._saver._results) == 3


async def start_save_process(p: Pilot):
    await p.click(f"#save-button")
    assert p.app.screen.name == "save"

    await p.click(f"#edit-save-path-button")
    assert p.app.screen.name == "path_edit"


async def edit_save_path(p: Pilot):
    tmp_tree_node = None
    for n in p.app.screen._directory_tree._tree_nodes.values():
        if "tmp" in n._label:
            tmp_tree_node = n
            break

    assert tmp_tree_node is not None
