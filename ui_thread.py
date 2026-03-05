import threading


def _has_after(window) -> bool:
    return hasattr(window, "after") and callable(getattr(window, "after"))


def _is_main_thread() -> bool:
    return threading.current_thread() is threading.main_thread()


def call_on_ui_thread(window, func, *args, wait: bool = True, **kwargs) -> None:
    """Execute func on Tk's UI thread when possible, otherwise run directly."""
    if _has_after(window) and not _is_main_thread():
        done = threading.Event()
        error = {"exc": None}

        def _runner() -> None:
            try:
                func(*args, **kwargs)
            except Exception as ex:  # pragma: no cover - defensive path
                error["exc"] = ex
            finally:
                done.set()

        window.after(0, _runner)
        if wait:
            done.wait()
            if error["exc"] is not None:
                raise error["exc"]
        return

    func(*args, **kwargs)


def set_var(window, var, value) -> None:
    call_on_ui_thread(window, var.set, value)


def set_bar_value(window, bar, value) -> None:
    call_on_ui_thread(window, bar.__setitem__, "value", value)


def update_idletasks(window) -> None:
    if hasattr(window, "update_idletasks"):
        call_on_ui_thread(window, window.update_idletasks)


def quit_window(window) -> None:
    if hasattr(window, "quit"):
        call_on_ui_thread(window, window.quit)
