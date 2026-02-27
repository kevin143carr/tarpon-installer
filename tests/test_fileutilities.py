from pathlib import Path

from fileutilities import FileUtilities


def test_modify_preserves_leading_whitespace(tmp_path: Path) -> None:
    target = tmp_path / "config.conf"
    target.write_text("    key = value\nother=1\n", encoding="utf-8")

    util = FileUtilities()
    util.modifyFileContents(str(target), "key = value", "key = new")

    assert target.read_text(encoding="utf-8") == "    key = new\nother=1\n"
