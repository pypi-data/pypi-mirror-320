import unittest
from swmm_api import SwmmInput, CONFIG
from swmm_api.input_file import SEC
from swmm_api.input_file.section_types import SECTION_TYPES
from swmm_api.input_file.sections import OptionSection


def create_test_function(section):
    """
    Dynamically create a test function for a specific section.
    """
    def test_function(self):
        content = ';...'  # Placeholder for an empty section in SWMM format
        inp = SwmmInput.read_text(f'[{section.upper()}]\n{content}\n')  # Create SwmmInput object
        if section == SEC.TITLE:
            # basically a string, so change
            self.assertEqual(inp._data.get(section), content)
            self.assertEqual(inp[section].to_inp_lines(), content)
        elif section == SEC.OPTIONS:
            # always converted, to look for infiltration method
            self.assertEqual(inp._data.get(section), OptionSection())
            self.assertEqual(inp[section].to_inp_lines(), CONFIG.comment_empty_section)
        else:
            self.assertEqual(inp._data.get(section), content)
            self.assertEqual(inp[section].to_inp_lines(), CONFIG.comment_empty_section)

    return test_function


class TestSwmmInputSections(unittest.TestCase):
    pass  # Placeholder for dynamically added test functions

# Dynamically add test functions for all sections
for sec in SECTION_TYPES:
    test_func = create_test_function(sec)
    test_func.__name__ = f'test_section_{sec}'  # Name the function for unittest reporting
    setattr(TestSwmmInputSections, test_func.__name__, test_func)  # Add the function to the class


if __name__ == '__main__':
    unittest.main()
