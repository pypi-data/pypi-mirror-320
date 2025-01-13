from pathlib import Path

import polars as pl
import pytest

from blackfish.parsing.exceptions import ParsingError
from blackfish.parsing.soc_absorption_spectrum import soc_absorption_spectrum

# Get the project root directory
ROOT = Path(__file__).parent


@pytest.fixture
def sample_soc_path():
    return ROOT / "data/soc_absorption_spectrum.txt"


def test_soc_absorption_spectrum_returns_dataframe(sample_soc_path):
    """Test that soc_absorption_spectrum function returns a polars DataFrame"""
    result = soc_absorption_spectrum(sample_soc_path)
    assert isinstance(result, pl.DataFrame)


def test_soc_absorption_spectrum_correct_columns(sample_soc_path):
    """Test that the returned DataFrame has the expected columns"""
    result = soc_absorption_spectrum(sample_soc_path)
    expected_columns = {
        "state",
        "mult",
        "energy_ev",
        "energy_cm",
        "wavelength_nm",
        "osc_strength",
        "d2",
        "dx",
        "dy",
        "dz",
        "rel_intensity",
    }
    assert set(result.columns) == expected_columns


def test_soc_absorption_spectrum_data_types(sample_soc_path):
    """Test that the columns have the correct data types"""
    result = soc_absorption_spectrum(sample_soc_path)
    assert result["state"].dtype == pl.Int64
    assert result["mult"].dtype == pl.Float64
    assert result["energy_ev"].dtype == pl.Float64
    assert result["energy_cm"].dtype == pl.Float64
    assert result["wavelength_nm"].dtype == pl.Float64
    assert result["osc_strength"].dtype == pl.Float64
    assert result["d2"].dtype == pl.Float64
    assert result["dx"].dtype == pl.Float64
    assert result["dy"].dtype == pl.Float64
    assert result["dz"].dtype == pl.Float64
    assert result["rel_intensity"].dtype == pl.Float64


def test_soc_absorption_spectrum_non_empty(sample_soc_path):
    """Test that the DataFrame is not empty"""
    result = soc_absorption_spectrum(sample_soc_path)
    assert len(result) > 0


def test_soc_absorption_spectrum_relative_intensity(sample_soc_path):
    """Test that relative intensity is correctly calculated"""
    result = soc_absorption_spectrum(sample_soc_path)
    # Relative intensity should be between 0 and 1
    assert all(0 <= x <= 1 for x in result["rel_intensity"])
    # Maximum relative intensity should be 1.0
    assert max(result["rel_intensity"]) == pytest.approx(1.0)
    # Check calculation for first row
    first_row = result.row(0)
    expected_rel_intensity = first_row[5] / result["osc_strength"].max()
    assert first_row[10] == pytest.approx(expected_rel_intensity)


def test_soc_absorption_spectrum_energy_wavelength_relationship(sample_soc_path):
    """Test that energy and wavelength values are consistent"""
    result = soc_absorption_spectrum(sample_soc_path)
    # Check that energy_cm = 1e7/wavelength_nm relationship holds
    for row in result.iter_rows():
        assert row[3] == pytest.approx(1e7 / row[4], rel=1e-2)


def test_soc_absorption_spectrum_state_mult_parsing(sample_soc_path):
    """Test that state and multiplicity are correctly parsed"""
    result = soc_absorption_spectrum(sample_soc_path)
    # States should be positive integers
    assert all(isinstance(x, int) and x > 0 for x in result["state"])
    # Multiplicities should be positive
    assert all(x > 0 for x in result["mult"])


def test_soc_absorption_spectrum_invalid_file():
    """Test that function raises error for non-existent file"""
    with pytest.raises(FileNotFoundError):
        soc_absorption_spectrum(Path("nonexistent_file.txt"))


def test_soc_absorption_spectrum_missing_header(tmp_path):
    """Test that function raises ParsingError when header is missing"""
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("Some random content\nwithout proper header")

    with pytest.raises(ParsingError):
        soc_absorption_spectrum(invalid_file)


def test_soc_absorption_spectrum_empty_data(tmp_path):
    """Test that function raises ParsingError when no data follows header"""
    invalid_file = tmp_path / "invalid.txt"
    header = "SOC CORRECTED ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS"
    invalid_file.write_text(f"{header}\n\n\n\n\n\n")

    with pytest.raises(ParsingError):
        soc_absorption_spectrum(invalid_file)


def test_soc_absorption_spectrum_physical_constraints(sample_soc_path):
    """Test that physical quantities satisfy basic constraints"""
    result = soc_absorption_spectrum(sample_soc_path)
    # Wavelengths should be positive
    assert all(x > 0 for x in result["wavelength_nm"])
    # Energies should be positive
    assert all(x > 0 for x in result["energy_ev"])
    assert all(x > 0 for x in result["energy_cm"])
    # Oscillator strengths should be non-negative
    assert all(x >= 0 for x in result["osc_strength"])
