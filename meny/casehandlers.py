from abc import abstractclassmethod
from typing import Any, Dict, Iterable, List, Optional
import meny
from meny.exceptions import MenuError
from ast import literal_eval
from inspect import getfullargspec, unwrap
from types import FunctionType
from meny.infos import _error_info_case
from meny.exceptions import MenuError


def _handle_args(func: FunctionType, args: Iterable[str]) -> List:
    """
    Handles list of strings that are the arguments using ast.literal_eval.

    E.g. return is [1, "cat", 2.0, False]
                   int  str   float  bool
    """
    # Unwrap in case the function is wrapped
    func = unwrap(func)
    argsspec = getfullargspec(func)
    params = argsspec.args

    if len(args) > len(params):
        raise MenuError(f"Got too many arguments, should be {len(params)}, but got {len(args)}")

    typed_arglist = [None] * len(args)
    try:
        for i, arg in enumerate(args):
            typed_arglist[i] = literal_eval(arg)
    except (ValueError, SyntaxError) as e:
        raise MenuError(
            f"Got arguments: {args}\n" f"But could not evaluate argument at position {i}:\n\t {arg}"
        ) from e
    return typed_arglist


def _handle_casefunc(casefunc: FunctionType, args: List[str], menu: meny.Menu) -> Any:
    program_args = menu.case_args.get(casefunc, ())
    program_kwargs = menu.case_kwargs.get(casefunc, {})
    if program_args or program_kwargs:  # If programmatic arguments
        if args:
            raise MenuError(
                "This function takes arguments progammatically" " and should not be given any arguments"
            )
        return casefunc(*program_args, **program_kwargs)
    elif args:
        # Raises TypeError if wrong number of arguments
        return casefunc(*_handle_args(casefunc, args))
    else:
        # Will raise TypeError if casefunc() actually requires arguments
        return casefunc()


class _CaseHandler:
    @classmethod
    def __call__(cls, menu: meny.Menu, casefunc: FunctionType, args: List[str]) -> None:
        # TODO: Should I catch TypeError in the handlers? What if actual TypeError occurs?
        #       Maybe should catch everything and just display it in big red text? Contemplate!
        try:
            cls.onCall(menu, casefunc, args)
        except (TypeError, MenuError) as e:
            _error_info_case(e, casefunc)
        finally:
            cls.afterCallReturn(menu, casefunc, args)

    @abstractclassmethod
    def onCall(cls, menu: meny.Menu, casefunc: FunctionType, args: List[str]) -> None:
        """
        Responsibility:
            Call casefunc
            Do whatever else to enforce handler behavior (related to unittests)
        """

    @abstractclassmethod
    def afterCallReturn(cls, menu: meny.Menu, casefunc: FunctionType, args: List[str]) -> None:
        """
        Responsibility:
            Hook for clean up after calling method
        """


class _TreeHandler(_CaseHandler):
    _stack: List[dict] = []

    @classmethod
    def onCall(cls, menu: meny.Menu, casefunc: FunctionType, args: List[str]):
        if len(cls._stack) == 0:
            cls._stack.append({})
        this_scope = cls._stack[-1]  # Get scope of current cls
        next_scope = this_scope.get(casefunc.__name__, {})  # Create / get next scope
        this_scope[casefunc.__name__] = next_scope  # Insert next scope into old scope
        cls._stack.append(next_scope)
        next_scope["return"] = _handle_casefunc(casefunc, args, menu)

    @classmethod
    def afterCallReturn(cls, menu: meny.Menu, casefunc: FunctionType, args: List[str]):
        cls._stack.pop()
        type(menu)._return = cls._stack[-1].copy()  # Set current return scope to previous


class _FlatHandler(_CaseHandler):
    _return: dict = {}

    @classmethod
    def onCall(cls, menu: meny.Menu, casefunc: FunctionType, args: List[str]):
        cls._return[casefunc.__name__] = _handle_casefunc(casefunc, args, menu)

    @classmethod
    def afterCallReturn(cls, menu: meny.Menu, casefunc: FunctionType, args: List[str]):
        type(menu)._return = cls._return
