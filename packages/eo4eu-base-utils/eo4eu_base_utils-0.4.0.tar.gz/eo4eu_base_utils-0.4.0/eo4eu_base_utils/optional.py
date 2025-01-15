import functools
from importlib.util import find_spec

from .utils import if_none


def _broken_func(error: str):
    raise ImportError(error)


def _get_broken_func(error: str):
    return functools.partial(_broken_func, error)


class BrokenClass:
    ERROR = ""

    def __init__(self, *args, **kwargs):
        raise ImportError(self.__class__.ERROR)


class OptionalModule:
    def __init__(
        self,
        package: str,
        enabled_by: list[str],
        depends_on: list[str]
    ):
        self._package = package
        self._enabled_by = enabled_by
        self._depends_on = depends_on

    def is_enabled(self) -> bool:
        if len(self._depends_on) == 0:
            return True

        return all([
            find_spec(dep) is not None
            for dep in self._depends_on
        ])

    def _error_message(self, name: str) -> str:
        preamble = f"{name} is not included in the base install of {self._package}."
        if len(self._enabled_by) == 0:
            return preamble

        submodule_blurb = ""
        if len(self._enabled_by) == 1:
            submodule_blurb = f"{self._package}[{self._enabled_by[0]}]"
        else:
            head, tail = self._enabled_by[:-1], self._enabled_by[-1]
            submodule_blurb = ", ".join([
                f"{self._package}[{submodule}]"
                for submodule in head
            ]) + f" or {self._package}[{tail}]"

        return f"{preamble} Please enable using {submodule_blurb}."

    def broken_class(self, name: str, class_attrs: list[str]|None = None):
        class_attrs = if_none(class_attrs, [])

        result = type(
            name,
            (BrokenClass,),
            {attr: _get_broken_func(self._error_message(name)) for attr in class_attrs}
        )
        result.ERROR = self._error_message(name)
        return result

    def broken_func(self, name: str):
        return _get_broken_func(self._error_message(name))
