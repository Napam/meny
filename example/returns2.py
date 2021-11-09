"""
POC use case of case functions that returns values
"""

import meny
import json

meny.set_default_once(False)


def returnsOne():
    return 1


def returnsTwo():
    return 2


vals1 = meny.menu(locals(), "MENU 1")
# vals2 = meny.menu(locals(), "MENU 2")
print(json.dumps(vals1, indent=4))
# print(json.dumps(vals2, indent=4))
