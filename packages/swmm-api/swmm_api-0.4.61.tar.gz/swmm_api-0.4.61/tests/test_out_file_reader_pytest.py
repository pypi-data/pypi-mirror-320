import pytest
from swmm_api import read_out_file, SwmmOutput
from swmm_api.output_file import OBJECTS, VARIABLES


@pytest.fixture
def swmm_output():
    """Fixture to load the SWMM output file."""
    return read_out_file('epaswmm5_apps_manual/Example6-Final.out')


def test_start_and_end_times(swmm_output):
    """Test slicing with start and end times."""
    start_i = 123
    end_i = 982
    start = swmm_output.index[start_i]
    end = swmm_output.index[end_i]

    # Check sliced index range
    sliced_index = swmm_output.index[start_i:end_i + 1]
    assert sliced_index[0] == start
    assert sliced_index[-1] == end


def test_slim_and_non_slim_reading(swmm_output):
    """Test slim vs non-slim data reading at specific start and end."""
    start_i = 123
    end_i = 982
    start = swmm_output.index[start_i]
    end = swmm_output.index[end_i]

    # Slim=True, start only
    swmm_output._frame = None
    swmm_output._data = None
    d = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, start=start)
    assert d.index[0] == start
    assert d.index[-1] == swmm_output.index[-1]

    # Slim=False, start only
    swmm_output._frame = None
    swmm_output._data = None
    d = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=start)
    assert d.index[0] == start
    assert d.index[-1] == swmm_output.index[-1]

    # Slim=True, end only
    swmm_output._frame = None
    swmm_output._data = None
    d = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, end=end)
    assert d.index[0] == swmm_output.index[0]
    assert d.index[-1] == end

    # Slim=False, end only
    d = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, end=end)
    assert d.index[0] == swmm_output.index[0]
    assert d.index[-1] == end


def test_data_reading_specific_time_range(swmm_output):
    """Test data reading for a specific time range."""
    start_i = 123
    end_i = 982
    start = swmm_output.index[start_i]
    end = swmm_output.index[end_i]

    d_slim = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True, start=start, end=end)
    d_non_slim = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=start, end=end)

    # Validate start and end indices for slim and non-slim versions
    assert d_slim.index[0] == start
    assert d_slim.index[-1] == end
    assert d_non_slim.index[0] == start
    assert d_non_slim.index[-1] == end


def test_full_data_reading(swmm_output):
    """Test full data reading with slim=True and slim=False."""
    d_slim = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=True)
    d_non_slim = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False)

    # Ensure data was read correctly
    assert not d_slim.empty, "Expected non-empty dataframe for slim=True"
    assert not d_non_slim.empty, "Expected non-empty dataframe for slim=False"


def test_partial_data_reading(swmm_output):
    """Test reading data with only start or end specified."""
    start_i = 123
    end_i = 982
    start = swmm_output.index[start_i]
    end = swmm_output.index[end_i]

    # Start only
    d_start_only = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, start=start)
    assert d_start_only.index[0] == start

    # End only
    d_end_only = swmm_output.get_part(OBJECTS.NODE, None, VARIABLES.NODE.HEAD, slim=False, end=end)
    assert d_end_only.index[-1] == end
