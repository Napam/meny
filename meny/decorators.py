from types import FunctionType

from meny.config import _CASE_IGNORE, _CASE_TITLE


def title(title: str):
    """
    Sets case title
    """

    def _title_appender(func: FunctionType):
        vars(func)[_CASE_TITLE] = title
        return func

    if isinstance(title, str):
        return _title_appender
    else:
        raise ValueError(f"Got unsupported type: {type(title)}")


def ignore(func: FunctionType):
    """
    Will flag case to be filtered out from menu creation
    """
    vars(func)[_CASE_IGNORE] = None  # Will only check for membership
    return func


if __name__ == "__main__":

    @title("Catdog")
    def testFunc1() -> str:
        pass

    @title("Catdog1")
    def testFunc2() -> str:
        pass

    print(vars(testFunc1))
    print(vars(testFunc2))
