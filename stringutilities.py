
from typing import Callable, Mapping


class StringUtilities:
    def _replace_tokens(self, text: str, values: Mapping[str, object], value_getter: Callable[[object], str]) -> str:
        for key, raw_value in values.items():
            token = f"%{key}%"
            if token not in text:
                continue
            replacement = value_getter(raw_value)
            while token in text:
                text = text.replace(token, replacement, 1)
        return text

    def checkForUserInput(self, text: str, userinputs) -> str:
        return self._replace_tokens(text, userinputs, lambda v: v.get())

    # The return value will either be what is in userinput or variables or original string sent in
    def checkForUserVariable(self, text: str, ini_info) -> str:
        if "%username%" in text and getattr(ini_info, "username", ""):
            text = text.replace("%username%", ini_info.username)
        text = self._replace_tokens(text, ini_info.userinput, lambda v: v.get())
        text = self._replace_tokens(text, ini_info.variables, lambda v: v)
        text = self._replace_tokens(text, ini_info.returnvars, lambda v: v)
        return text
