import threading

import pytest

from ui_thread import call_on_ui_thread


class DummyWindow:
    def after(self, _delay_ms, callback) -> None:
        callback()


def test_call_on_ui_thread_reraises_system_exit_from_worker_thread() -> None:
    captured = {}

    def worker() -> None:
        try:
            call_on_ui_thread(DummyWindow(), lambda: (_ for _ in ()).throw(SystemExit(1)))
        except BaseException as ex:  # pragma: no cover - assertion target
            captured["exc"] = ex

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    assert isinstance(captured.get("exc"), SystemExit)
    assert captured["exc"].code == 1
