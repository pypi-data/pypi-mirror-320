from pathlib import Path

import polars as pl
import pytest

from blackfish.parsing.exceptions import ParsingError
from blackfish.parsing.nacme import nacme

ROOT = Path(__file__).parent


@pytest.fixture
def sample_nacme_path():
    return ROOT / "data/nacme.txt"


def test_nacme_returns_dataframe(sample_nacme_path):
    """Test that nacme function returns a polars DataFrame"""
    result = nacme(sample_nacme_path)
    assert isinstance(result, pl.DataFrame)


def test_nacme_correct_columns(sample_nacme_path):
    """Test that the returned DataFrame has the expected columns"""
    result = nacme(sample_nacme_path)
    expected_columns = {"id", "symbol", "x", "y", "z", "magnitude"}
    assert set(result.columns) == expected_columns


def test_nacme_data_types(sample_nacme_path):
    """Test that the columns have the correct data types"""
    result = nacme(sample_nacme_path)
    assert result["id"].dtype == pl.Int64
    assert result["symbol"].dtype == pl.String
    assert result["x"].dtype == pl.Float64
    assert result["y"].dtype == pl.Float64
    assert result["z"].dtype == pl.Float64
    assert result["magnitude"].dtype == pl.Float64


def test_nacme_non_empty(sample_nacme_path):
    """Test that the DataFrame is not empty"""
    result = nacme(sample_nacme_path)
    assert len(result) > 0


def test_nacme_magnitude_calculation(sample_nacme_path):
    """Test that magnitude is correctly calculated"""
    result = nacme(sample_nacme_path)
    # Test for first row
    first_row = result.row(0)
    expected_magnitude = abs(first_row[2]) + abs(first_row[3]) + abs(first_row[4])
    assert first_row[5] == pytest.approx(expected_magnitude)


def test_nacme_invalid_file():
    """Test that function raises error for non-existent file"""
    with pytest.raises(FileNotFoundError):
        nacme(Path("nonexistent_file.txt"))


def test_nacme_invalid_content(tmp_path):
    """Test handling of file without expected header"""
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("Some random content\nwithout proper header")

    with pytest.raises(ParsingError):
        nacme(invalid_file)
