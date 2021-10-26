import unittest
import meny as meny

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
            meny.utils._assert_supported(
                "dog", "animal", ("dog", "rabbit")
            )  # Shuold be no error
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

        args2 = meny._menu._handle_args(function, [repr(arg) for arg in args])
        self.assertListEqual(args, args2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
