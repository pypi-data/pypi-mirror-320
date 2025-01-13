from pathlib import Path

import polars as pl
import pytest

from blackfish.parsing.exceptions import ParsingError
from blackfish.parsing.ir_spectrum import ir_spectrum

ROOT = Path(__file__).parent


@pytest.fixture
def sample_ir_path():
    return ROOT / "data/ir_spectrum.txt"


def test_ir_spectrum_returns_dataframe(sample_ir_path):
    """Test that ir_spectrum function returns a polars DataFrame"""
    result = ir_spectrum(sample_ir_path)
    assert isinstance(result, pl.DataFrame)


def test_ir_spectrum_correct_columns(sample_ir_path):
    """Test that the returned DataFrame has the expected columns"""
    result = ir_spectrum(sample_ir_path)
    expected_columns = {
        "mode",
        "frequency_cm",
        "epsilon",
        "intensity",
        "t2",
        "tx",
        "ty",
        "tz",
        "rel_intensity",
    }
    assert set(result.columns) == expected_columns


def test_ir_spectrum_data_types(sample_ir_path):
    """Test that the columns have the correct data types"""
    result = ir_spectrum(sample_ir_path)
    assert result["mode"].dtype == pl.Int64
    assert result["frequency_cm"].dtype == pl.Float64
    assert result["epsilon"].dtype == pl.Float64
    assert result["intensity"].dtype == pl.Float64
    assert result["t2"].dtype == pl.Float64
    assert result["tx"].dtype == pl.Float64
    assert result["ty"].dtype == pl.Float64
    assert result["tz"].dtype == pl.Float64
    assert result["rel_intensity"].dtype == pl.Float64


def test_ir_spectrum_non_empty(sample_ir_path):
    """Test that the DataFrame is not empty"""
    result = ir_spectrum(sample_ir_path)
    assert len(result) > 0


def test_ir_spectrum_relative_intensity(sample_ir_path):
    """Test that relative intensity is correctly calculated"""
    result = ir_spectrum(sample_ir_path)
    # Relative intensity should be between 0 and 1
    assert all(0 <= x <= 1 for x in result["rel_intensity"])
    # Maximum relative intensity should be 1.0
    assert max(result["rel_intensity"]) == pytest.approx(1.0)
    # Check calculation for first row
    first_row = result.row(0)
    expected_rel_intensity = first_row[3] / result["intensity"].max()
    assert first_row[8] == pytest.approx(expected_rel_intensity)


def test_ir_spectrum_invalid_file():
    """Test that function raises error for non-existent file"""
    with pytest.raises(FileNotFoundError):
        ir_spectrum(Path("nonexistent_file.txt"))


def test_ir_spectrum_missing_header(tmp_path):
    """Test that function raises ParsingError when header is missing"""
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("Some random content\nwithout proper header")

    with pytest.raises(ParsingError):
        ir_spectrum(invalid_file)


def test_ir_spectrum_data_format(sample_ir_path):
    """Test that the data is properly formatted"""
    result = ir_spectrum(sample_ir_path)
    # All modes should be positive integers
    assert all(x > 0 for x in result["mode"])
    # All frequencies should be positive - what about imaginary frequencies?
    # assert all(x > 0 for x in result["frequency_cm"])
    # All intensities should be non-negative
    assert all(x >= 0 for x in result["intensity"])
