from iniinfo import iniInfo
from stringutilities import StringUtilities


class DummyVar:
    def __init__(self, value: str) -> None:
        self._value = value

    def get(self) -> str:
        return self._value


def test_check_for_user_variable_replaces_all_sources() -> None:
    info = iniInfo()
    info.userinput = {"userdata": DummyVar("UVAL")}
    info.variables = {"var": "VVAL"}
    info.returnvars = {"ret": "RVAL"}
    info.hostname = "10.0.0.5"

    util = StringUtilities()
    result = util.checkForUserVariable("path %userdata% %var% %ret% %host%", info)

    assert result == "path UVAL VVAL RVAL 10.0.0.5"
