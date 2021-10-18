import unittest
import meny as meny


class TestUtils(unittest.TestCase):
    def test__extract_and_preprocess_functions(self):
        """list_local_cases manages to get functions"""

        class Dummy:
            pass

        def linear(x: int):
            return 2 * x

        def quadratic(x: int):
            return x * x

        def cubic(x: int):
            return x * x * x

        cases = meny.utils._extract_and_preprocess_functions(locals())
        self.assertListEqual(cases, [linear, quadratic, cubic])

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

        args = meny.input_splitter(" ".join(inputlist))
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
