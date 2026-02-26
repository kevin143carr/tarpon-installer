from pathlib import Path

from iniinfo import iniInfo
from task import Task


class DummyWindow:
    def update_idletasks(self) -> None:
        return None


class DummyVar:
    def __init__(self) -> None:
        self.value = ""

    def set(self, value: str) -> None:
        self.value = value


def test_copy_from_resources_local_copies_file(tmp_path: Path) -> None:
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    (resources_dir / "file.txt").write_text("hello", encoding="utf-8")

    dest_dir = tmp_path / "out"
    dest_file = dest_dir / "file.txt"

    info = iniInfo()
    info.resources = "resources"
    info.buildtype = "LINUX"
    info.installtype = "LOCAL"
    info.files = {"file.txt": str(dest_file)}

    task = Task(info)
    bar = {}
    taskitem = DummyVar()
    window = DummyWindow()

    # Run in tmp_path to mimic app cwd
    cwd = Path.cwd()
    try:
        import os
        os.chdir(tmp_path)
        task.copyFromResourcesLocal(window, bar, taskitem, info)
    finally:
        os.chdir(cwd)

    assert dest_file.exists()
    assert dest_file.read_text(encoding="utf-8") == "hello"
