import logging
from pathlib import Path

from iniinfo import iniInfo
from tarpon_installer import HeadlessVar, setup_logging, setup_headless_inputs


def test_setup_headless_inputs_applies_alsocheckoption_dependencies() -> None:
    info = iniInfo()
    info.options = {
        "option_prepare_workspace": "ALSOCHECKOPTION::option_show_summary,option_exec_python::Prepare workspace",
        "option_show_summary": "Show completion summary",
        "option_exec_python": "Execute Python callback popup",
    }
    info.userinput = {}

    setup_headless_inputs(
        info,
        userinput_overrides={},
        enabled_options=["option_prepare_workspace"],
        logger=logging.getLogger("test"),
    )

    assert isinstance(info.optionvals["option_prepare_workspace"], HeadlessVar)
    assert info.optionvals["option_prepare_workspace"].get() == "1"
    assert info.optionvals["option_show_summary"].get() == "1"
    assert info.optionvals["option_exec_python"].get() == "1"


def test_setup_logging_with_liveviewlog_adds_stream_handler(tmp_path: Path) -> None:
    config_path = tmp_path / "headless.ini"
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    try:
        setup_logging(str(config_path), "INFO", liveviewlog=True)
        handler_types = {type(handler).__name__ for handler in logging.getLogger().handlers}
        assert "FileHandler" in handler_types
        assert "StreamHandler" in handler_types
    finally:
        for handler in list(logging.getLogger().handlers):
            handler.close()
        logging.getLogger().handlers.clear()
        for handler in original_handlers:
            logging.getLogger().addHandler(handler)
