import unittest
import pypatconsole as ppc 

class TestUtils(unittest.TestCase):
    def test_list_local_cases(self):
        """list_local_cases manages to get functions"""
        class Dummy:
            pass

        def linear(x: int):
            return 2*x
        
        def quadratic(x: int):
            return x*x
        
        def cubic(x: int):
            return x*x*x

        cases = ppc.list_local_cases(locals())
        self.assertEqual(len(cases), 3)
        self.assertIs(cases[0], linear)
        self.assertIs(cases[1], quadratic)
        self.assertIs(cases[2], cubic)

    def test_input_splitter(self):
        """input_splitter parses input correctly"""
        inputlist = ["12", "abcd", '("1, 2", 3)', '["1, 2", 3]', 
                     '{"hello": "world", 666:"number of the beast"}', '{"set", "of", "strings"}',
                     "'apostrophe string'"]

        args = ppc.input_splitter(" ".join(inputlist))
        self.assertEqual(inputlist, args)

if __name__ == '__main__':
    unittest.main(verbosity=2)