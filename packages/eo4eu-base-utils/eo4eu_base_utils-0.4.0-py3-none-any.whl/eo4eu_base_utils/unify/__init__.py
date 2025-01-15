import re
from types import UnionType
from ..typing import Any, Union, Dict, Iterable, get_origin, get_args
from ..result import Result


def overlay(lhs: Any, rhs: Any) -> Any:
    if isinstance(lhs, list) and isinstance(rhs, list):
        return lhs + rhs

    if not (isinstance(lhs, dict) and isinstance(rhs, dict)):
        return rhs

    result = {key: val for key, val in lhs.items()}
    for key, val in rhs.items():
        if key not in result:
            result[key] = val
        else:
            result[key] = overlay(result[key], val)

    return result


def get_recursively(d: dict, path: list[str]) -> Any:
    result = d
    for key in path:
        result = result[key]
    return result


def set_recursively(d: dict, path: list[str], val: Any):
    result = d
    head, tail = path[:-1], path[-1]
    for key in head:
        result = result[key]
    result[tail] = val


class UnifyError(Exception):
    pass


def _unify_error(path: list[str], blurb: str):
    full_key = ".".join(path)
    if len(path) == 0:
        full_key = "."
    return Result.err(f"Key \"{full_key}\": {blurb}")


def _unify_types[T](lhs: Iterable[type], rhs: T, path: list[str], name: str) -> Result[T]:
    if isinstance(rhs, type) and (rhs not in lhs):
        return _unify_error(path, f"Type \"{rhs}\" incompatible with value \"{name}\"")
    elif not isinstance(rhs, lhs):
        return _unify_error(path, f"Value \"{rhs}\" incompatible with type \"{name}\"")
    return Result.ok(rhs)


def _unify_simple[T,V](lhs: T, rhs: V, path: list[str]) -> Result[T|V]:
    if lhs != rhs:
        return _unify_error(path, f"Value \"{rhs}\" incompatible with \"{lhs}\"")
    return Result.ok(rhs)


def _unify_regex[T](lhs: re.Pattern, rhs: T, path: list[str]) -> Result[T]:
    if isinstance(rhs, re.Pattern):
        return _unify_scalar(lhs.pattern, rhs.patterns, path)
    if isinstance(rhs, str):
        if re.fullmatch(rhs) is None:
            return _unify_error(path, f"Value \"{rhs}\" incompatible with pattern \"{lhs.pattern}\"")
        return Result.ok(rhs)

    return _unify_error(path, f"Value \"{rhs}\" of type \"{rhs.__class__.__name__}\" cannot "
                              f"be matched to \"{lhs.pattern}\"")


def _unify_scalar_one_side[T,V](lhs: T, rhs: V, path: list[str]) -> tuple[Result[T|V],bool]:
    if isinstance(lhs, type):
        return (_unify_types((lhs,), rhs, path, str(lhs.__name__)), True)
    if get_origin(lhs) in (Union, UnionType):
        return (_unify_types(get_args(lhs), rhs, path, str(lhs)), True)
    if isinstance(lhs, re.Pattern):
        return (_unify_regex(lhs, rhs, path), True)
    return (None, False)


def _unify_scalar[T,V](lhs: T, rhs: V, path: list[str]) -> Result[T|V]:
    result, ok = _unify_scalar_one_side(lhs, rhs, path)
    if not ok:
        result, ok = _unify_scalar_one_side(rhs, lhs, path)
    if not ok:
        return _unify_simple(lhs, rhs, path)
    return result


def _unify_dict(lhs: dict, rhs: Any, path: list[str], exit_on_err: bool = False) -> Result[dict]:
    if not isinstance(rhs, Dict):
        return _unify_error(path, f"Value \"{rhs}\" incompatible with type \"dict\"")

    result_dict = {key: val for key, val in lhs.items()}
    error_stack = []
    for key, val in rhs.items():
        if key not in result_dict:
            result_dict[key] = val
        elif isinstance(val, Dict):
            unify_res = _unify_dict(result_dict[key], val, path + [key])
            if unify_res.is_ok():
                result_dict[key] = unify_res.get()
            else:
                error_stack.extend(unify_res.stack())
                if exit_on_err:
                    break
        else:
            unify_res = _unify_scalar(result_dict[key], val, path + [key])
            if unify_res.is_ok():
                result_dict[key] = unify_res.get()
            else:
                error_stack.extend(unify_res.stack())
                if exit_on_err:
                    break

    return Result(
        is_ok = len(error_stack) == 0,
        value = result_dict,
        stack = error_stack
    )


def _unify[T,V](lhs: T, rhs: V, path: list[str], **kwargs) -> Result[T|V]:
    if isinstance(lhs, Dict):
        return _unify_dict(lhs, rhs, path, **kwargs)
    if isinstance(rhs, Dict):
        return _unify_dict(rhs, lhs, path, **kwargs)
    return _unify_scalar(lhs, rhs, path)


def unify(lhs: Any, rhs: Any, unwrap = True, **kwargs) -> Any:
    result = _unify(lhs, rhs, [], **kwargs)
    if unwrap:
        return result.unwrap(exc_class = UnifyError)
    return result
