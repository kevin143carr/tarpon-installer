import logging
from pathlib import Path

from iniinfo import iniInfo
from tarpon_installer import (
    HeadlessVar,
    build_headless_summary_lines,
    prompt_for_headless_userinput,
    setup_logging,
    setup_headless_inputs,
)


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


def test_setup_headless_inputs_prompts_when_userinput_has_no_default(monkeypatch, capsys) -> None:
    prompts = []
    info = iniInfo()
    info.userinput = {
        "customer_name": "Enter customer shortname",
    }
    info.userinput_defaults = {}
    info.options = {}

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: prompts.append(prompt) or "acme",
    )

    setup_headless_inputs(
        info,
        userinput_overrides={},
        enabled_options=[],
        logger=logging.getLogger("test"),
    )

    output = capsys.readouterr()
    assert "USER INPUT REQUIRED" in output.out
    assert "Enter customer shortname" in output.out
    assert prompts == ["Enter value: "]
    assert info.userinput["customer_name"].get() == "acme"


def test_setup_headless_inputs_uses_defaults_and_overrides_without_prompting(monkeypatch) -> None:
    info = iniInfo()
    info.userinput = {
        "customer_name": "Enter customer shortname",
        "environment": "Enter environment",
    }
    info.userinput_defaults = {
        "customer_name": "acme",
        "environment": "qa",
    }
    info.options = {}

    def fail_input(_: str) -> str:
        raise AssertionError("input() should not be called")

    monkeypatch.setattr("builtins.input", fail_input)

    setup_headless_inputs(
        info,
        userinput_overrides={"environment": "prod"},
        enabled_options=[],
        logger=logging.getLogger("test"),
    )

    assert info.userinput["customer_name"].get() == "acme"
    assert info.userinput["environment"].get() == "prod"


def test_prompt_for_headless_userinput_retries_blank_values(monkeypatch, capsys) -> None:
    responses = iter(["", "acme"])
    prompts = []
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: prompts.append(prompt) or next(responses),
    )

    value = prompt_for_headless_userinput("Enter customer shortname")

    output = capsys.readouterr()
    assert "USER INPUT REQUIRED" in output.out
    assert prompts == ["Enter value: ", "Enter value: "]
    assert value == "acme"


def test_setup_headless_inputs_prompts_when_override_is_blank_and_no_default(monkeypatch, capsys) -> None:
    prompts = []
    info = iniInfo()
    info.userinput = {
        "customer_name": "Enter customer shortname",
    }
    info.userinput_defaults = {}
    info.options = {}

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: prompts.append(prompt) or "acme",
    )

    setup_headless_inputs(
        info,
        userinput_overrides={"customer_name": ""},
        enabled_options=[],
        logger=logging.getLogger("test"),
    )

    output = capsys.readouterr()
    assert "USER INPUT REQUIRED" in output.out
    assert prompts == ["Enter value: "]
    assert info.userinput["customer_name"].get() == "acme"


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


def test_build_headless_summary_lines_includes_active_options_and_prompts() -> None:
    info = iniInfo()
    info.installtitle = "Headless Test"
    info.buttontext = "Run Install"
    info.buildtype = "LINUX"
    info.installtype = "LOCAL"
    info.resources = "."
    info.options = {
        "option_prepare_workspace": "Prepare workspace",
        "option_extra_message": "Show extra message",
    }
    info.optionvals = {
        "option_prepare_workspace": HeadlessVar("1"),
        "option_extra_message": HeadlessVar("0"),
    }
    info.userinput = {
        "customer_name": HeadlessVar("acme"),
        "environment": HeadlessVar("qa"),
    }
    info.actions = {
        "action_confirm": "YESNO::Proceed with install?::echo go",
        "action_message": "MSGBOX::Important maintenance notice",
        "action_if_then_else": "[IF]%environment% == qa[THEN]MSGBOX::QA branch selected[ELSE]MSGBOX::Non-QA branch selected",
        "action_role": "POPLIST::Pick deployment role::INPUTLIST::Admin,PowerUser::selected_role",
        "option_extra_message": "MSGBOX::This should not appear",
    }
    info.finalactions = {}

    lines = build_headless_summary_lines("example.ini", info)
    summary = "\n".join(lines)

    assert "Config file: example.ini" in summary
    assert "Install title: Headless Test" in summary
    assert "Action prompt: Run Install" in summary
    assert "Enabled options:\n- option_prepare_workspace" in summary
    assert "- customer_name = acme" in summary
    assert "- environment = qa" in summary
    assert "- YESNO: Proceed with install?" in summary
    assert "- MSGBOX: Important maintenance notice" in summary
    assert "- MSGBOX: QA branch selected" in summary
    assert "- POPLIST: Pick deployment role" in summary
    assert "This should not appear" not in summary
