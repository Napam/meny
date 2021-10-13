from types import FunctionType

_CASE_TITLE = "_case_title"
_DEFINITION_ORDER = "_definition_order"
__counter = 0


def case(title: str):
    def _case_wrapper(func: FunctionType):
        func.__dict__[_CASE_TITLE] = title
        func.__dict__[_DEFINITION_ORDER] = __counter
        return func

    if isinstance(title, str):
        global __counter
        __counter += 1
        return _case_wrapper
    else:
        raise ValueError(f"Got unsupported type: {type(title)}")


if __name__ == '__main__':
    @case("Catdog")
    def testFunc1() -> str:
        pass
    
    @case("Catdog1")
    def testFunc2() -> str:
        pass

    print(testFunc1.__dict__)
    print(testFunc2.__dict__)