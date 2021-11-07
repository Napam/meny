"""
POC use case of case functions that returns values
"""

import meny


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


vals = meny.menu(locals())
print(vals)
