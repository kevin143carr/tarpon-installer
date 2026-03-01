from pathlib import Path

import pytest

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


def test_modify_files_local_add_expands_returnvars_for_existing_file(tmp_path: Path) -> None:
    target_file = tmp_path / "generated.conf"
    target_file.write_text("existing=true\n", encoding="utf-8")

    info = iniInfo()
    info.installtype = "LOCAL"
    info.buildtype = "LINUX"
    info.returnvars = {"selected_role": "Admin"}
    info.modify = {
        "1": f"{{FILE}}{target_file}{{ADD}}role=%selected_role%"
    }

    task = Task(info)
    bar = {}
    taskitem = DummyVar()
    window = DummyWindow()

    task.modifyFilesLocal(window, bar, taskitem, info)

    assert target_file.read_text(encoding="utf-8") == "existing=true\nrole=Admin\n"


def test_copy_from_resources_local_raises_on_copy_error_when_continuewitherrors_is_false(
    tmp_path: Path,
    monkeypatch,
) -> None:
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    (resources_dir / "file.txt").write_text("hello", encoding="utf-8")

    info = iniInfo()
    info.resources = "resources"
    info.buildtype = "LINUX"
    info.installtype = "LOCAL"
    info.continuewitherrors = False
    info.files = {"file.txt": str(tmp_path / "out" / "file.txt")}

    task = Task(info)
    bar = {}
    taskitem = DummyVar()
    window = DummyWindow()

    monkeypatch.setattr("task.copyfile", lambda src, dst: (_ for _ in ()).throw(PermissionError("Access is denied.")))

    cwd = Path.cwd()
    try:
        import os
        os.chdir(tmp_path)
        with pytest.raises(PermissionError):
            task.copyFromResourcesLocal(window, bar, taskitem, info)
    finally:
        os.chdir(cwd)


def test_copy_from_resources_local_continues_on_copy_error_when_continuewitherrors_is_true(
    tmp_path: Path,
    monkeypatch,
    caplog,
) -> None:
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    (resources_dir / "file1.txt").write_text("hello", encoding="utf-8")
    (resources_dir / "file2.txt").write_text("world", encoding="utf-8")

    info = iniInfo()
    info.resources = "resources"
    info.buildtype = "LINUX"
    info.installtype = "LOCAL"
    info.continuewitherrors = True
    info.files = {
        "file1.txt": str(tmp_path / "out" / "file1.txt"),
        "file2.txt": str(tmp_path / "out" / "file2.txt"),
    }

    task = Task(info)
    bar = {}
    taskitem = DummyVar()
    window = DummyWindow()

    original_copyfile = __import__("task").copyfile

    def flaky_copyfile(src, dst):
        if src.endswith("file1.txt"):
            raise PermissionError("Access is denied.")
        return original_copyfile(src, dst)

    monkeypatch.setattr("task.copyfile", flaky_copyfile)

    cwd = Path.cwd()
    try:
        import os
        os.chdir(tmp_path)
        with caplog.at_level("ERROR", logger="logger"):
            task.copyFromResourcesLocal(window, bar, taskitem, info)
    finally:
        os.chdir(cwd)

    assert "Error copying file file1.txt: Access is denied." in caplog.text
    assert (tmp_path / "out" / "file2.txt").read_text(encoding="utf-8") == "world"
