import unittest
from swmm_api import SwmmOutput
from swmm_api.output_file import OBJECTS, VARIABLES
import pandas.testing as pdt
import numpy.testing as npt


class TestSwmmOutput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the SWMM output file for all tests."""
        cls.out = SwmmOutput('../examples/epaswmm5_apps_manual/Example6-Final.out')
        cls.start_i = 123
        cls.end_i = 982
        cls.start = cls.out.index[cls.start_i]
        cls.end = cls.out.index[cls.end_i]

    def test_times(self):
        """Test slicing with start and end times."""
        sliced_index = self.out.index[self.start_i:self.end_i + 1]
        self.assertEqual(sliced_index[0], self.start)
        self.assertEqual(sliced_index[-1], self.end)

    def test_start_s(self):
        """Test slim=True data reading from a specific start time."""
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, start=self.start, show_progress=False)
        self.assertEqual(d.index[0], self.start)
        self.assertEqual(d.index[-1], self.out.index[-1])

    def test_start(self):
        """Test slim=False data reading from a specific start time without preliminary results."""
        self.out._data = None
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=self.start)
        self.assertEqual(d.index[0], self.start)
        self.assertEqual(d.index[-1], self.out.index[-1])

    def test_start_p(self):
        """Test slim=False data reading from a specific start time with preliminary results."""
        self.out.to_numpy()  # preliminary results saved for slim=False
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=self.start)
        self.assertEqual(d.index[0], self.start)
        self.assertEqual(d.index[-1], self.out.index[-1])

    def test_start_c(self):
        """Test compare data reading from a specific start time with slim=True and slim=False without preliminary results."""
        self.out._data = None
        d1 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=self.start)
        d2 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, start=self.start, show_progress=False)
        pdt.assert_frame_equal(d1, d2)

    def test_start_pc(self):
        """Test compare data reading from a specific start time with slim=True and slim=False with preliminary results."""
        self.out.to_numpy()  # preliminary results saved for slim=False
        d1 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=self.start)
        d2 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, start=self.start, show_progress=False)
        pdt.assert_frame_equal(d1, d2)

    def test_end_s(self):
        """Test slim=True data reading up to a specific end time."""
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, end=self.end, show_progress=False)
        self.assertEqual(d.index[0], self.out.index[0])
        self.assertEqual(d.index[-1], self.end)

    def test_end(self):
        """Test slim=False data reading up to a specific end time without preliminary results."""
        self.out._data = None
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, end=self.end)
        self.assertEqual(d.index[0], self.out.index[0])
        self.assertEqual(d.index[-1], self.end)

    def test_end_p(self):
        """Test slim=False data reading up to a specific end time with preliminary results."""
        self.out.to_numpy()  # preliminary results saved for slim=False
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, end=self.end)
        self.assertEqual(d.index[-1], self.end)
        self.assertEqual(d.index[0], self.out.index[0])

    def test_end_c(self):
        """Test compare data reading up to a specific end time with slim=True and slim=False without preliminary results."""
        self.out._data = None
        d1 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, end=self.end)
        d2 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, end=self.end, show_progress=False)
        pdt.assert_frame_equal(d1, d2)

    def test_end_pc(self):
        """Test compare data reading up to a specific end time with slim=True and slim=False with preliminary results."""
        self.out.to_numpy()  # preliminary results saved for slim=False
        d1 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, end=self.end)
        d2 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, end=self.end, show_progress=False)
        pdt.assert_frame_equal(d1, d2)

    def test_part_s(self):
        """Test slim=True data reading for a specific time range."""
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, start=self.start, end=self.end, show_progress=False)
        self.assertEqual(d.index[0], self.start)
        self.assertEqual(d.index[-1], self.end)

    def test_part(self):
        """Test slim=False data reading for a specific time range without preliminary results."""
        self.out._data = None
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=self.start, end=self.end)
        self.assertEqual(d.index[0], self.start)
        self.assertEqual(d.index[-1], self.end)

    def test_part_p(self):
        """Test slim=False data reading for a specific time range with preliminary results."""
        self.out.to_numpy()  # preliminary results saved for slim=False
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=self.start, end=self.end)
        self.assertEqual(d.index[0], self.start)
        self.assertEqual(d.index[-1], self.end)

    def test_part_c(self):
        """Test compare data reading for a specific time range with slim=True and slim=False without preliminary results."""
        self.out._data = None
        d1 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=self.start, end=self.end)
        d2 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, start=self.start, end=self.end, show_progress=False)
        pdt.assert_frame_equal(d1, d2)

    def test_part_pc(self):
        """Test compare data reading for a specific time range with slim=True and slim=False with preliminary results."""
        self.out.to_numpy()  # preliminary results saved for slim=False
        d1 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=self.start, end=self.end)
        d2 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, start=self.start, end=self.end, show_progress=False)
        pdt.assert_frame_equal(d1, d2)

    def test_full(self):
        """Test slim=False data reading for the full time range."""
        self.out._data = None
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False)
        self.assertFalse(d.empty, "Expected non-empty dataframe for slim=False")
        self.assertEqual(d.index[-1], self.out.index[-1])
        self.assertEqual(d.index[0], self.out.index[0])

    def test_full_s(self):
        """Test slim=True data reading for the full time range."""
        d = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, show_progress=False)
        self.assertFalse(d.empty, "Expected non-empty dataframe for slim=True")
        self.assertEqual(d.index[-1], self.out.index[-1])
        self.assertEqual(d.index[0], self.out.index[0])

    def test_full_c(self):
        """Test compare data reading for the full time range with slim=True and slim=False."""
        self.out._data = None
        d1 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False)
        d2 = self.out.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, show_progress=False)
        pdt.assert_frame_equal(d1, d2)


if __name__ == '__main__':
    unittest.main()
