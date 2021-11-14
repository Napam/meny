import unittest
import meny as meny
import random


class TestUtils(unittest.TestCase):
    def test__extract_and_preprocess_functions(self):
        """_extract_and_preprocess_functions manages to extract functions from locals() in correct order"""

        class Dummy:
            pass

        def linear(x: int):
            return 2 * x

        def quadratic(x: int):
            return x * x

        def cubic(x: int):
            return x * x * x

        def func1():
            pass

        def func2():
            pass

        def func3():
            pass

        cases = meny.utils._extract_and_preprocess_functions(locals())
        self.assertListEqual(cases, [linear, quadratic, cubic, func1, func2, func3])

    def test_input_splitter(self):
        """input_splitter parses input correctly"""
        inputlist = [
            "..",
            "12",
            "abcd",
            '("1, 2", 3)',
            '["1, 2", 3]',
            '{"hello": "world", 666:"number of the beast"}',
            '{"set", "of", "strings"}',
            "'apostrophe string'",
            '"quote string"',
            "-123",
        ]

        args = meny.input_splitter(" \t  \b".join(inputlist))
        self.assertSetEqual(set(inputlist), set(args))

    def test_RE_ANSI(self):
        """RE_ANSI manages to match ANSI escape characters"""
        string = "\x1b[31mRed\x1b[0m \033[32mGreen\033[0m \x1b[36mBlue\033[0m \nTo be erased\x1b[2K"
        output = meny.utils.RE_ANSI.sub("", string)
        self.assertEqual(output, "Red Green Blue \nTo be erased")

    def test__assert_supported(self):
        with self.assertRaises(AssertionError):
            meny.utils._assert_supported("cat", "animal", ("dog", "rabbit"))

        gotException = False
        try:
            meny.utils._assert_supported("dog", "animal", ("dog", "rabbit"))  # Shuold be no error
        except AssertionError:
            gotException = True
        self.assertFalse(gotException)

    def test_set_default_frontend(self):
        """set_default_frontend works for simple, fancy, auto and only those"""
        meny.set_default_frontend("simple")
        self.assertEqual(meny.config.DEFAULT_FRONTEND, "simple")
        meny.set_default_frontend("fancy")
        self.assertEqual(meny.config.DEFAULT_FRONTEND, "fancy")
        meny.set_default_frontend("auto")
        self.assertEqual(meny.config.DEFAULT_FRONTEND, "auto")

        with self.assertRaises(AssertionError):
            meny.set_default_frontend("bingbongdingdong")

        with self.assertRaises(AssertionError):
            meny.set_default_frontend("electricboogaloo")

        with self.assertRaises(AssertionError):
            meny.set_default_frontend("gunsnroses")

    def test_set_default_once(self):
        """set_default_frontend works for simple, fancy, auto and only those"""
        meny.set_default_once(False)
        self.assertFalse(meny.config.DEFAULT_ONCE)
        meny.set_default_once(True)
        self.assertTrue(meny.config.DEFAULT_ONCE)

        with self.assertRaises(AssertionError):
            meny.set_default_frontend("bingbongdingdong")

        with self.assertRaises(AssertionError):
            meny.set_default_frontend(123)

        with self.assertRaises(AssertionError):
            meny.set_default_frontend("gunsnroses")

    def test__handle_args(self):
        """
        _handle_args evaluates strings to correct types
        """

        def function(a, b, c, d, e, f, g, h):
            pass

        args = [
            "hehe",
            12,
            123.0,
            True,
            {"dictionary": 123},
            ("t", "u", "p", "l", 3),
            ["l", 1, 5, "t"],
            {"s", "e", "t"},
        ]

        args2 = meny.casehandlers._handle_args(function, [repr(arg) for arg in args])
        self.assertListEqual(args, args2)

    def test__funcmap_output(self):
        """
        Test funcmap output
        """

        def abba():
            pass

        def mamma():
            pass

        def mia():
            pass

        funcs = random.choices([abba, mamma, mia], k=64)
        funcmap = meny._menu.construct_funcmap(funcs)
        self.assertEqual(len(funcs), len(funcmap))
        self.assertListEqual([str(i) for i in range(1, len(funcs) + 1)], list(funcmap.keys()))
        for f, kv in zip(funcs, funcmap.values()):
            self.assertIsInstance(kv[0], str)
            self.assertIs(f, kv[1])

    def test__TreeHandler(self):
        """
        _TreeHandler returns correct tree structure
        """

        class DummyMenu:
            _return = None

            def __init__(self):
                self.case_args = {}
                self.case_kwargs = {}

        dum = DummyMenu()

        handler = meny.casehandlers._TreeHandler()

        def func1(val=0):
            if val == 2:
                return val
            handler(dum, func2, [f"{val+1}"])
            return val

        def func2(val=0):
            if val == 2:
                return val
            handler(dum, func1, [f"{val+1}"])
            return val

        handler(dum, func1, [])
        returns = {"func1": {"func2": {"func1": {"return": 2}, "return": 1}, "return": 0}}
        self.assertDictEqual(returns, handler._stack[0])

    def test__FlatHandler(self):
        """
        _FlatHandler returns correct flat structure
        """

        class DummyMenu:
            _return = None

            def __init__(self):
                self.case_args = {}
                self.case_kwargs = {}

        dum = DummyMenu()

        handler = meny.casehandlers._FlatHandler()

        def func1(val=0):
            if val == 2:
                return val
            handler(dum, func2, [f"{val+1}"])
            return val

        def func2(val=0):
            if val == 2:
                return val
            handler(dum, func1, [f"{val+1}"])
            return val

        handler(dum, func1, [])
        returns = {"func1": 0, "func2": 1}
        self.assertDictEqual(returns, handler._return)

    def test__handle_casefunc(self):
        """Handle casfunc works as expected"""

        class DummyMenu:
            def __init__(self):
                self.case_args = {}
                self.case_kwargs = {}

        menu = DummyMenu()

        def func(a, b, c):
            return (a, b, c)

        returns = meny._handle_casefunc(func, ["1", "2", "3"], menu)
        self.assertTupleEqual(returns, (1, 2, 3))

        with self.assertRaises(TypeError):
            meny._handle_casefunc(func, [], menu)

        with self.assertRaises(TypeError):
            meny._handle_casefunc(func, ["1", "2"], menu)

        menu.case_args = {func: (1, 2)}

        with self.assertRaises(meny.MenuError):
            meny._handle_casefunc(func, ["1", "2", "3"], menu)

        menu.case_kwargs = {func: {"c": 4}}
        returns = meny._handle_casefunc(func, [], menu)
        self.assertTupleEqual(returns, (1, 2, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
