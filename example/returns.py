"""
Isolated example of return values
"""

import meny
import json


def returnsOne():
    def returnsTwo():
        return "2"

    meny.menu(locals())
    return "1"


def returnsOne2():
    def returnsTwo():
        return 2

    meny.menu(locals())
    return 1


vals1 = meny.menu(locals(), "MENU 1", return_mode="tree")
input("Press enter to start MENU 2")
vals2 = meny.menu(locals(), "MENU 2", return_mode="flat")
print(json.dumps(vals1, indent=4))
print(json.dumps(vals2, indent=4))
