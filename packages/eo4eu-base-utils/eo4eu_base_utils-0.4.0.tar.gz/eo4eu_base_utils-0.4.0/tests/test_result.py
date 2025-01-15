from eo4eu_base_utils.typing import get_args
from eo4eu_base_utils.result import Result

from typing import get_type_hints


def _describe(instance):
    cls = instance.__class__
    print(cls, get_args(cls))


def _invert(num):
    return -num


def _add_6(num):
    return num + 6


def test_annot_0():
    def _to_positive(num: int) -> Result[int]:
        if num > 0:
            return Result[int].ok(num)
        else:
            return Result.err(f"Number {num} is not positive")

    n0 = 2
    n1 = 6
    n3 = 0
    n4 = -7

    p0 = _to_positive(n0)
    p3 = _to_positive(n3)
    print(p0, p3)
    print(p0.map_ok(_invert), p3.map_ok(_invert))
    print(p0.map_all(_invert, _add_6), p3.map_all(_invert, _add_6).map_err(lambda _: 7))
    # _describe(p0)
    # _describe(p3)
    # _describe(Result.ok(6))
    # print(get_args(Result[int]))
    # print(get_type_hints(_to_positive))
    # print(get_type_hints(Result.ok))
    # print(get_type_hints(Result.err))
    # print(get_type_hints(Result.wrap))
    # print(get_type_hints(Result.merge))


if __name__ == "__main__":
    test_annot_0()
