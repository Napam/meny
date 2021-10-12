from types import FunctionType


_CASE_TITLE = "_case_title"
__counter = 0

def _get_case_wrapper(title: str):
    def _case_wrapper(func: FunctionType):
        func.__dict__[_CASE_TITLE] = title
        return func
    return _case_wrapper


def case(title: str, enforce_order: bool = False):
    if isinstance(title, str):
        global __counter 
        __counter += 1
        print(__counter)

        return _get_case_wrapper(title)
    else:
        raise ValueError(f"Got unsupported type: {type(title)}")


if __name__ == '__main__':
    @case("Catdog")
    def testFunc() -> str:
        pass

    print(testFunc.__dict__)