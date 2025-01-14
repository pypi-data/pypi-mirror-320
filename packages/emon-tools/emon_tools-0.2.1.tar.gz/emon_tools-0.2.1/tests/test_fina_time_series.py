"""
Unit tests for the FinaDataFrame and FinaDfStats classes.

This module contains pytest-based tests
for the FinaDataFrame and FinaDfStats classes,
which provide methods to represent results
as a pandas DataFrame or plot them using
matplotlib.
"""
# pylint: disable=unused-argument,protected-access,unused-import
from unittest.mock import patch, mock_open
from struct import pack
import numpy as np
import pandas as pd
import pytest
from emon_tools.fina_time_series import FinaDataFrame
from emon_tools.fina_utils import Utils
from emon_tools.fina_time_series import FinaDfStats
from emon_tools.emon_fina import StatsType


class TestFinaDataFrame:
    """
    Unit tests for the FinaDataFrame class.
    """
    @pytest.fixture
    def tmp_path_override(self, tmp_path):
        """
        Provide a fixture for a valid temporary path
        to simulate data directory.
        """
        data_dir = tmp_path / "test_data"
        data_dir.mkdir()
        return str(data_dir)

    @pytest.fixture
    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<2I", 10, 1575981140))
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    def fdt(self,
            mock_open_file,
            mock_isfile,
            mock_getsize,
            tmp_path_override):
        """
        Fixture to provide a valid FinaData instance for testing.
        """
        feed_id = 1
        return FinaDataFrame(
            feed_id=feed_id,
            data_dir=tmp_path_override
        )

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_get_fina_df_time_series(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test get_fina_time_series method.
        """
        with pytest.raises(ValueError, match=r"^Invalid start value.*"):
            fdt.get_fina_df_time_series(
                start=1605983130,
                step=10,
                window=400
            )
        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs to mimic actual mmap slicing behavior
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                # Calculate the position based on the slice start
                # Number of floats
                size = (slice_obj.stop - slice_obj.start) // 4
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method
        data = fdt.get_fina_df_time_series(
            start=1575981140,
            step=10,
            window=100
        )
        assert isinstance(data, pd.DataFrame)
        assert data['values'].shape[0] == 10

        # Run the read_file method
        data = fdt.get_fina_df_time_series(
            start=1575981140,
            step=20,
            window=100
        )

        assert isinstance(data, pd.DataFrame)
        assert data['values'].shape[0] == 5

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_get_fina_time_series_by_date(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test get_fina_values_by_date method.
        """
        start, end = Utils.get_dates_interval_from_timestamp(
            start=1605983130,
            window=400
        )
        with pytest.raises(ValueError, match=r"^Invalid start value.*"):
            fdt.get_fina_time_series_by_date(
                start_date=start,
                end_date=end,
                step=10
            )
        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs to mimic actual mmap slicing behavior
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                # Calculate the position based on the slice start
                # Number of floats
                size = (slice_obj.stop - slice_obj.start) // 4
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method
        start, end = Utils.get_dates_interval_from_timestamp(
            start=1575981140,
            window=100
        )
        data = fdt.get_fina_time_series_by_date(
            start_date=start,
            end_date=end,
            step=10
        )

        assert isinstance(data, pd.DataFrame)
        assert data['values'].shape[0] == 10

        # Run the read_file method
        data = fdt.get_fina_time_series_by_date(
            start_date=start,
            end_date=end,
            step=20
        )

        assert isinstance(data, pd.DataFrame)
        assert data['values'].shape[0] == 5

    @pytest.mark.parametrize(
        "times, values, expected_exception, error_msg",
        [
            (
                "invalid", np.array([3600]), ValueError,
                'Times and Values must be a numpy ndarray.'
            ),
            (
                np.array([3600]), 'invalid', ValueError,
                'Times and Values must be a numpy ndarray.'
            ),
            (
                np.array([3600]), np.array([3600, 160]), ValueError,
                'Times and Values must have same shape.'
            ),
        ],
    )
    def test_set_data_frame_exceptions(
        self,
        times,
        values,
        expected_exception,
        error_msg
    ):
        """Test exceptions for set_data_frame."""
        with pytest.raises(expected_exception, match=error_msg):
            FinaDataFrame.set_data_frame(times, values)


class TestFinaDfStats:
    """
    Unit tests for the FinaDfStats class.
    """
    @pytest.fixture
    def tmp_path_override(self, tmp_path):
        """
        Provide a fixture for a valid temporary path
        to simulate data directory.
        """
        data_dir = tmp_path / "test_data"
        data_dir.mkdir()
        return str(data_dir)

    @pytest.fixture
    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<2I", 10, 1575981140))
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    def fds(
        self,
        mock_open_file,
        mock_isfile,
        mock_getsize,
        tmp_path_override
    ):
        """
        Fixture to provide a valid FinaDfStats instance for testing.
        """
        feed_id = 1
        return FinaDfStats(
            feed_id=feed_id,
            data_dir=tmp_path_override
        )

    @patch.object(FinaDfStats, 'get_stats', return_value=[
        [1575981140, 1.0, 2.0, 3.0],
        [1575981200, 1.1, 2.1, 3.1]
    ])
    def test_get_df_stats(self, mock_get_stats, fds):
        """
        Test get_df_stats method.
        """
        df = fds.get_df_stats(
            start_time=1575981140,
            steps_window=60,
            stats_type=StatsType.VALUES
        )
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 2
        assert list(df.columns) == ['time', 'min', 'mean', 'max']

    @patch.object(FinaDfStats, 'get_stats_by_date', return_value=[
        [1575981140, 1.0, 2.0, 3.0],
        [1575981200, 1.1, 2.1, 3.1]
    ])
    def test_get_df_stats_by_date(self, mock_get_stats_by_date, fds):
        """
        Test get_df_stats_by_date method.
        """
        df = fds.get_df_stats_by_date(
            start_date="2023-01-01 00:00:00",
            end_date="2023-01-02 00:00:00",
            stats_type=StatsType.VALUES
        )
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 2
        assert list(df.columns) == ['time', 'min', 'mean', 'max']

    def test_get_stats_labels(self, fds):
        """
        Test get_stats_labels method.
        """
        labels = fds.get_stats_labels(stats_type=StatsType.VALUES)
        assert labels == ['time', 'min', 'mean', 'max']

        labels = fds.get_stats_labels(stats_type=StatsType.INTEGRITY)
        assert labels == ['time', 'nb_finite', 'nb_total']

    def test_get_integrity_labels(self):
        """
        Test get_integrity_labels method.
        """
        labels = FinaDfStats.get_integrity_labels()
        assert labels == ['time', 'nb_finite', 'nb_total']

    def test_get_values_labels(self):
        """
        Test get_values_labels method.
        """
        labels = FinaDfStats.get_values_labels()
        assert labels == ['time', 'min', 'mean', 'max']

