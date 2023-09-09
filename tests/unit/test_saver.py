from os import chdir

from recoverpy.lib.saver import Saver


def test_add(tmp_path):
    saver = Saver()

    saver.add_result(1, "test1")
    saver.add_result(2, "test2")
    saver.add_result(0, "test0")

    assert saver.get_blocks_to_save_count() == 3


def test_reset(tmp_path):
    saver = Saver()

    saver.add_result(1, "test1")
    saver.add_result(2, "test2")
    saver.add_result(0, "test0")
    saver.reset_results()

    assert saver.get_blocks_to_save_count() == 0


def test_update_save_path(tmp_path):
    saver = Saver()

    saver.set_save_path(str(tmp_path))
    assert saver.save_path == tmp_path


def test_get_selected_blocks_count(tmp_path):
    saver = Saver()

    saver.add_result(1, "test1")
    saver.add_result(2, "test2")
    saver.add_result(0, "test0")

    assert saver.get_blocks_to_save_count() == 3


def test_save(tmp_path):
    saver = Saver()

    saver.set_save_path(str(tmp_path))
    saver.add_result(1, "test1")
    saver.add_result(2, "test2")
    saver.add_result(0, "test0")
    saver.save_results()

    assert saver.last_saved_file in list(tmp_path.iterdir())
    with open(saver.last_saved_file, "r") as f:
        assert f.read().splitlines() == ["test0", "test1", "test2"]


def test_save_no_path(tmp_path):
    chdir(tmp_path)
    saver = Saver()

    saver.add_result(1, "test1")
    saver.save_results()

    assert saver.last_saved_file in list(tmp_path.iterdir())
