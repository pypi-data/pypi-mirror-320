from eo4eu_base_utils.unify import unify, overlay


def test_overlay_0():
    d0 = {"a": 1, "b": 2, "c": {"d": 4, "e": 5}}
    d1 = {"a": -1, "c": {"e": -5, "f": -6}, "g": -7}

    print("test_overlay_0")
    print(overlay(d0, d1))
    print(overlay(d1, d0))


def test_overlay_1():
    d0 = {"a": 1, "b": [2,3,4]}
    d1 = {"a": -1, "b": [5,6,7]}

    print("test_overlay_1")
    print(overlay(d0, d1))
    print(overlay(d1, d0))


def test_unify_0():
    scm = {"a": int, "b": {"c": object, "d": str|None}}
    val0 = {"a": 5, "b": {"c": "smth", "d": "hello"}}
    val1 = {"a": 5.1, "b": {"c": 17, "d": -0.4}}

    print(unify(scm, val0))
    print(unify(scm, val1, unwrap = False).fmt_err())
    print(unify(scm, val1, unwrap = False, exit_on_err = True).fmt_err())


if __name__ == "__main__":
    test_overlay_0()
    test_overlay_1()
    test_unify_0()
