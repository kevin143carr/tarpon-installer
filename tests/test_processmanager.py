import logging

from managers.processmanager import ProcessManager


def test_log_subprocess_output_uses_error_level_for_stderr(caplog) -> None:
    process_manager = ProcessManager()

    with caplog.at_level(logging.INFO, logger="logger"):
        process_manager._log_subprocess_output("normal output", "error output")

    assert "normal output" in caplog.text
    assert "error output" in caplog.text
    stderr_record = next(record for record in caplog.records if record.message == "error output")
    assert stderr_record.levelno == logging.ERROR


def test_execute_procs_logs_failed_stdout_and_return_code_as_errors(monkeypatch, caplog) -> None:
    process_manager = ProcessManager()

    class FakePopen:
        def __init__(self, *args, **kwargs) -> None:
            self.pid = 1234
            self.returncode = 1

        def communicate(self, timeout=None):
            return ("Access is denied.", "")

    monkeypatch.setattr("managers.processmanager.subprocess.Popen", FakePopen)
    monkeypatch.setattr("managers.processmanager.time.sleep", lambda _: None)

    with caplog.at_level(logging.INFO, logger="logger"):
        result = process_manager.executeProcs("rmdir /S /Q C:\\JAAR\\support\\activemq")

    assert result == 1
    assert "ACTION FAILED COMMAND [rmdir /S /Q C:\\JAAR\\support\\activemq] RC [1]" in caplog.text
    error_records = [
        record for record in caplog.records
        if record.message == "Access is denied." and record.levelno == logging.ERROR
    ]
    assert error_records
