from typing import TypeVar, Union

from PySide6 import QtCore

T = TypeVar("T")


def read_bool_setting(settings: QtCore.QSettings, setting_name: str,
                      default: Union[bool, T] = False) -> Union[bool, T]:
    try:
        s = settings.value(setting_name)
        if s is not None:
            s_int = int(s)  # type: ignore
            return False if s_int == 0 else True
        else:
            return default
    except ValueError:
        return default


def read_int_setting(settings: QtCore.QSettings, setting_name: str,
                     default: Union[int, T] = 0) -> Union[int, T]:
    try:
        s = settings.value(setting_name)
        if s is not None:
            return int(s)  # type: ignore
        else:
            return default
    except ValueError:
        return default


def write_bool_setting(settings: QtCore.QSettings, setting_name: str,
                       value: bool) -> None:
    settings.setValue(setting_name, 1 if value else 0)
