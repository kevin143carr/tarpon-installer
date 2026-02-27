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


class DummyInput:
    def __init__(self, value: str) -> None:
        self.value = value

    def get(self) -> str:
        return self.value


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


def test_copy_from_resources_local_expands_tokens_for_linux(tmp_path: Path) -> None:
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    (resources_dir / "file.txt").write_text("hello", encoding="utf-8")

    info = iniInfo()
    info.resources = "resources"
    info.buildtype = "LINUX"
    info.installtype = "LOCAL"
    info.variables = {"stagedir": str(tmp_path / "out")}
    info.userinput = {
        "customer_name": DummyInput("acme"),
        "environment": DummyInput("qa"),
    }
    info.files = {"file.txt": "%stagedir%/%customer_name%/%environment%"}

    task = Task(info)
    bar = {}
    taskitem = DummyVar()
    window = DummyWindow()

    cwd = Path.cwd()
    try:
        import os
        os.chdir(tmp_path)
        task.copyFromResourcesLocal(window, bar, taskitem, info)
    finally:
        os.chdir(cwd)

    dest_file = tmp_path / "out" / "acme" / "qa" / "file.txt"
    assert dest_file.exists()
    assert dest_file.read_text(encoding="utf-8") == "hello"
