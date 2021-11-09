"""
POC use case of case functions that returns values
"""

import meny
import json

meny.set_default_once(False)


def returnsOne():
    def returnsTwo():
        def returnsThree():
            return 3

        def returnsOne():
            return 111

        meny.menu(locals())
        return 2

    meny.menu(locals())
    return 1


def returnsOne2():
    def returnsTwo():
        def returnsThree():
            return 3

        def returnsOne():
            return 111

        meny.menu(locals())
        return 2

    meny.menu(locals())
    return 1


vals1 = meny.menu(locals(), "MENU 1")
# vals2 = meny.menu(locals(), "MENU 2")
print(json.dumps(vals1, indent=4))
print(vals1)
# print(json.dumps(vals2, indent=4))

a = {
    "returnsOne": {"value": 1, "returnsTwo": {"value": 2, "returnsThree": {"value": 3}}},
    "returnsOne2": {"value": 1, "returnsTwo": {"value": 2, "returnsThree": {"value": 3}}},
}
