import logging
import traceback

from ..typing import Self, Any, List, Callable, TypeVar


T = TypeVar("T")
V = TypeVar("V")
W = TypeVar("W")


class Result[T]:
    PRINT_EXCEPTIONS = False
    NDASH = 25

    def __init__(self, is_ok: bool, value: T, stack: list[str]):
        self._is_ok = is_ok
        self._value = value
        self._stack = stack

    @classmethod
    def none(cls) -> "Result[None]":
        return Result(is_ok = False, value = None, stack = [])

    @classmethod
    def ok(cls, value: V, stack: list[str]|None = None) -> "Result[V]":
        if stack is None:
            stack = []
        return Result(is_ok = True, value = value, stack = stack)

    @classmethod
    def err(cls, error: str|List[str], value: V = None) -> "Result[V]":
        stack = error
        if not isinstance(error, list):
            stack = [error]
        if cls.PRINT_EXCEPTIONS:
            fmt_exc = traceback.format_exc()
            if fmt_exc != "NoneType: None":
                stack[-1] += "\n".join([
                    f"\n{cls.NDASH*'-'} BEGIN EXCEPTION {cls.NDASH*'-'}",
                    fmt_exc,
                    f"{cls.NDASH*'-'}- END EXCEPTION -{cls.NDASH*'-'}\n",
                ])
        return Result(is_ok = False, value = value, stack = stack)

    @classmethod
    def wrap(self, func: Callable[[Any],V], *args, **kwargs) -> "Result[V|None]":
        try:
            return Result.ok(func(*args, **kwargs))
        except Exception as e:
            return Result.err(str(e))

    # @classmethod
    # def all_of(self, input: "List[Result[V]]") -> "Result[List[Result[V]]]":
    #     stack = []
    #     for item in input:
    #         stack.extend(item.stack())
    #         if item.is_err():
    #             return Result(
    #                 is_ok = False,
    #                 value = input,
    #                 stack = item.stack()
    #             )
    #     return Result.ok(input, stack = stack)

    # @classmethod
    # def any_of(self, input: "List[Result[V]]") -> "Result[List[Result[V]]]":
    #     stack = []
    #     for item in input:
    #         stack.extend(item.stack())
    #         if item.is_ok():
    #             return Result.ok(input)

    #     return Result.err(stack, value = input)

    @classmethod
    def merge_all(self, input: "Iterator[Result[V]]") -> "Result[List[V]]":
        result = []
        for item in input:
            if item.is_err():
                return item
            result.append(item.get())
        return Result.ok(result)

    @classmethod
    def merge_any(self, input: "Iterator[Result[V]]") -> "Result[List[V]]":
        result = []
        stack = []
        for item in input:
            if item.is_ok():
                result.append(item.get())
            else:
                stack.extend(item.stack())

        if len(result) == 0:
            return Result.err(stack)
        else:
            return Result.ok(result)

    def is_ok(self) -> bool:
        return self._is_ok

    def is_err(self) -> bool:
        return not self._is_ok

    def stack(self) -> List[str]:
        return self._stack

    def copy(self) -> "Result[T]":
        return Result(self.is_ok(), self.get(), self.stack())

    def log(self, logger: logging.Logger, level: int = logging.WARNING) -> Self:
        for msg in self._stack:
            logger.log(level, msg)
        return self

    def then(self, other: "Result[V]") -> "Result[V]":
        return Result(
            is_ok = other.is_ok(),
            value = other.get(),
            stack = self._stack + other._stack
        )

    def then_ok(self, value: V) -> "Result[V]":
        return self.then(Result.ok(value))

    def then_err(self, error: str, value: V = None) -> "Result[T|V]":
        if value is None:
            value = self.get()
        return self.then(Result.err(error, value = value))

    def then_try(self, other: "Result[V]") -> "Result[T|V]":
        if other.is_ok():
            return self.then(other)
        else:
            return self

    def then_warn(self, *errors: str) -> "Result[T]":
        return Result(
            is_ok = self.is_ok(),
            value = self.get(),
            stack = self._stack + list(errors)
        )

    def default(self, default: V) -> "Result[T,V]":
        if self.is_err():
            return Result.ok(default)
        return self

    def pop_warning(self) -> tuple["Result[T]",str|None]:
        n_warn = len(self._stack)
        if n_warn == 0:
            return self, None

        result = self.copy()
        warning = result._stack.pop(n_warn - 1)
        return result, warning

    def fmt_err(self) -> str:
        return "\n".join(self._stack)

    def log_warnings(self, logger) -> Self:
        for msg in self._stack:
            logger.warning(msg)
        return self

    def get(self) -> T:
        return self._value

    def get_or(self, default: V) -> T|V:
        if self.is_err():
            return default
        return self.get()

    def unwrap(self, exc_class: Exception = ValueError) -> T:
        if self.is_err():
            raise exc_class(self.fmt_err())
        return self.get()

    def map(self, func: Callable[Any,V], *args, **kwargs) -> "Result[V|None]":
        return self.then(Result.wrap(func, *args, **kwargs))

    def map_ok(self, func: Callable[[T],V], *args, **kwargs) -> "Result[V|None]":
        if self.is_err():
            return self
        return self.map(func, self.get(), *args, **kwargs)

    def map_err(self, func: Callable[[str],V], *args, **kwargs) -> "Result[T|V]":
        if self.is_ok():
            return self

        result, last_warning = self.pop_warning()
        return result.map(func, last_warning, *args, **kwargs)

    def map_many(self, *funcs: Callable) -> "Result":
        if self.is_err():
            return self

        result = self.copy()
        for func in funcs:
            result = result.map_ok(func)
            if result.is_err():
                break
        return result

    def map_with(self, acc: Callable[[T,V],W], other: "Result[V]", *args, **kwargs) -> "Result[W]":
        if self.is_ok() and other.is_ok():
            return Result(
                is_ok = True,
                value = acc(self.get(), other.get(), *args, **kwargs),
                stack = self._stack + other._stack
            )
        else:
            return Result(
                is_ok = self.is_ok() or other.is_ok(),
                value = self.get() if self.is_ok() else other.get(),
                stack = self._stack + other._stack
            )

    def __repr__(self) -> str:
        modifier = "ok" if self.is_ok() else "err"
        return f"Result.{modifier}({self.get()})"
