from recoverpy.lib.saver import Saver


def test_save(tmp_path):
    saver = Saver()
    saver.update_save_path(str(tmp_path))
    saver.add(1, "test1")
    saver.add(2, "test2")
    saver.add(0, "test0")
    saver.save()

    assert saver.last_saved_file in list(tmp_path.iterdir())
    with open(saver.last_saved_file, "r") as f:
        assert f.read().splitlines() == ["test0", "test1", "test2"]

