from pathlib import Path

import plotly.graph_objects as go
import polars as pl
import pytest

from blackfish.structure import Structure

ROOT = Path(__file__).parent


@pytest.fixture
def sample_xyz_path():
    return ROOT / "data/structure.xyz"


@pytest.fixture
def sample_output_path():
    return ROOT / "data/structure.out"


@pytest.fixture
def temp_xyz_file(tmp_path):
    return tmp_path / "test.xyz"


def test_xyz_initialization():
    """Test Structure class initialization with a DataFrame"""
    data = [
        {"Symbol": "C", "X": 0.0, "Y": 0.0, "Z": 0.0},
        {"Symbol": "H", "X": 1.0, "Y": 0.0, "Z": 0.0},
    ]
    df = pl.DataFrame(data)
    structure = Structure(df)
    assert isinstance(structure.df, pl.DataFrame)
    assert len(structure.df) == 2


def test_from_xyz_file(sample_xyz_path):
    """Test creating Structure object from structure file"""
    structure = Structure.from_xyz_file(sample_xyz_path)
    assert isinstance(structure, Structure)
    assert isinstance(structure.df, pl.DataFrame)
    assert len(structure.df) > 0
    assert all(col in structure.df.columns for col in ["Symbol", "X", "Y", "Z"])


def test_parse_xyz_file(sample_xyz_path):
    """Test parsing structure file into DataFrame"""
    df = Structure.from_xyz_file(sample_xyz_path).df
    assert isinstance(df, pl.DataFrame)
    assert all(col in df.columns for col in ["Symbol", "X", "Y", "Z"])
    assert df.dtypes == [
        pl.Utf8,
        pl.Float64,
        pl.Float64,
        pl.Float64,
    ]


def test_write_xyz_file(temp_xyz_file):
    """Test writing Structure data to file"""
    data = [
        {"Symbol": "C", "X": 0.0, "Y": 0.0, "Z": 0.0},
        {"Symbol": "H", "X": 1.0, "Y": 0.0, "Z": 0.0},
    ]
    df = pl.DataFrame(data)
    structure = Structure(df)
    structure.to_xyz_file(temp_xyz_file)

    # Verify file exists and content is correct
    assert temp_xyz_file.exists()
    content = temp_xyz_file.read_text().splitlines()
    assert content[0] == "2"  # number of atoms
    assert content[1] == ""  # empty comment line
    assert len(content) == 4  # total lines (count + comment + 2 atoms)


def test_from_output_file(sample_output_path):
    """Test creating Structure object from ORCA output file"""
    structure = Structure.from_output_file(sample_output_path)
    assert isinstance(structure, Structure)
    assert isinstance(structure.df, pl.DataFrame)
    assert len(structure.df) > 0
    assert all(col in structure.df.columns for col in ["Symbol", "X", "Y", "Z"])


def test_parse_output_file(sample_output_path):
    """Test parsing ORCA output file into DataFrame"""
    df = Structure.parse_output_file(sample_output_path)
    assert isinstance(df, pl.DataFrame)
    assert all(col in df.columns for col in ["Symbol", "X", "Y", "Z"])
    assert df.dtypes == [
        pl.Utf8,
        pl.Float64,
        pl.Float64,
        pl.Float64,
    ]


def test_write_then_read_xyz(temp_xyz_file):
    """Test writing Structure file and reading it back gives same data"""
    original_data = [
        {"Symbol": "C", "X": 0.0, "Y": 0.0, "Z": 0.0},
        {"Symbol": "H", "X": 1.0, "Y": 0.0, "Z": 0.0},
    ]
    original_xyz = Structure(pl.DataFrame(original_data))
    original_xyz.to_xyz_file(temp_xyz_file)

    # Read back
    read_xyz = Structure.from_xyz_file(temp_xyz_file)

    # Compare DataFrames
    assert original_xyz.df.equals(read_xyz.df)


def test_xyz_file_not_found():
    """Test appropriate error is raised for non-existent files"""
    with pytest.raises(FileNotFoundError):
        Structure.from_xyz_file(Path("nonexistent.xyz"))


def test_invalid_xyz_file(tmp_path):
    """Test handling of invalid Structure file format"""
    invalid_file = tmp_path / "invalid.xyz"
    invalid_file.write_text("not a number\ncomment\nC 0 0 0")

    with pytest.raises(ValueError):
        Structure.from_xyz_file(invalid_file)


def test_detect_bonds_simple_molecule(sample_xyz_path):
    """Test bond detection for a simple molecule."""
    structure = Structure.from_xyz_file(sample_xyz_path)
    bonds = structure.detect_bonds()

    assert isinstance(bonds, list)
    assert all(isinstance(bond, tuple) for bond in bonds)
    assert all(len(bond) == 2 for bond in bonds)
    assert all(isinstance(i, int) and isinstance(j, int) for i, j in bonds)


def test_detect_bonds_tolerance():
    """Test that bond detection responds to tolerance parameter."""
    # Create a simple two-atom molecule
    data = [
        {"Symbol": "C", "X": 0.0, "Y": 0.0, "Z": 0.0},
        {"Symbol": "C", "X": 1.5, "Y": 0.0, "Z": 0.0},  # Typical C-C bond length
    ]
    structure = Structure(pl.DataFrame(data))

    # Should detect bond with default tolerance
    bonds_default = structure.detect_bonds(tolerance=1.2)
    assert len(bonds_default) == 1

    # Should not detect bond with very small tolerance
    bonds_strict = structure.detect_bonds(tolerance=0.5)
    assert len(bonds_strict) == 0

    # Should detect bond with larger tolerance
    bonds_loose = structure.detect_bonds(tolerance=2.0)
    assert len(bonds_loose) == 1


def test_detect_bonds_no_invalid_elements():
    """Test that bond detection handles invalid elements gracefully."""
    data = [
        {"Symbol": "C", "X": 0.0, "Y": 0.0, "Z": 0.0},
        {"Symbol": "Xx", "X": 1.5, "Y": 0.0, "Z": 0.0},  # Invalid element
    ]
    structure = Structure(pl.DataFrame(data))
    bonds = structure.detect_bonds()
    assert len(bonds) == 0  # Should not detect any bonds with invalid element


def test_plot_returns_figure():
    """Test that plot method returns a Plotly Figure object."""
    data = [
        {"Symbol": "C", "X": 0.0, "Y": 0.0, "Z": 0.0},
        {"Symbol": "H", "X": 1.0, "Y": 0.0, "Z": 0.0},
    ]
    structure = Structure(pl.DataFrame(data))
    fig = structure.plot()
    assert isinstance(fig, go.Figure)
