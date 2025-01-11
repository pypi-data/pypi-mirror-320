# Blackfish 🐋

Blackfish is a Python library for parsing and visualizing ORCA quantum chemistry output files. It provides an easy-to-use interface for extracting spectral data and generating publication-quality plots using Altair.

## Features

- Parse ORCA output files for:
  - IR spectra
  - Spin-orbit coupling (SOC) states
  - SOC absorption spectra
  - Non-adiabatic coupling matrix elements (NACME)
  - Electronic excited states
- Generate interactive visualizations:
  - IR spectra plots
  - SOC absorption spectra with Gaussian broadening
  - Peak detection and labeling
- Interactive UI components using Marimo for spectrum analysis

## Installation

```bash
pip install blackfish
```

## Quick Start

```python
from blackfish import ORCA

# Load ORCA output file
orca = ORCA("my_calculation.out")

# Access different types of data as Polars DataFrames
ir_data = orca.ir_spectrum
soc_data = orca.soc_states
nacme_data = orca.nacme
roots_data = orca.roots
absorption_data = orca.soc_absorption_spectrum

# Get SOC absorption spectrum with Gaussian broadening
soc_chart = orca.soc_absorption_spectrum_chart(
    fwhm=2000,       # Gaussian broadening FWHM
    peaks=True,      # Show peak markers
    peak_threshold=0.3  # Minimum peak threshold
)
```

## Examples

### IR Spectrum Analysis

```python
# Get IR spectrum data
ir_data = orca.ir_spectrum

# View strongest vibrational modes
strongest_modes = ir_data.filter(pl.col("rel_intensity") > 0.5)
print(strongest_modes)

# Get frequencies above 3000 cm⁻¹
high_freq = ir_data.filter(pl.col("frequency_cm") > 3000)
print(high_freq)
```

### Electronic State Analysis

```python
# Get excited state data
roots = orca.roots

# Group transitions by multiplicity
by_mult = roots.group_by("mult").agg([
    pl.count(),
    pl.mean("energy_cm").alias("avg_energy")
])
```

### SOC States Analysis

```python
# Get SOC states
soc = orca.soc_states

# Get contributions to specific SOC state
state1 = soc.filter(pl.col("state") == 1)

# Find states with large spin mixing
mixed_states = soc.filter(pl.col("weight") > 0.2)

# Summarize spin components per state
spin_summary = soc.group_by("state").agg([
    pl.n_unique("spin").alias("n_spin_components"),
    pl.max("weight").alias("max_contribution")
])
```

### NACME Analysis

```python
# Get non-adiabatic coupling elements
nacme = orca.nacme

# Find atoms with strong coupling
strong_coupling = nacme.filter(pl.col("magnitude") > 0.1)

# Get coupling vectors for specific atoms
h_atoms = nacme.filter(pl.col("symbol") == "H")

# Sort atoms by coupling magnitude
sorted_coupling = nacme.sort("magnitude", descending=True)
```

### SOC Absorption Spectrum Analysis

```python
# Get absorption spectrum
abs_spec = orca.soc_absorption_spectrum

# Find intense transitions
intense = abs_spec.filter(pl.col("rel_intensity") > 0.5)

# Get visible region transitions
visible = abs_spec.filter(
    (pl.col("wavelength_nm") >= 380) &
    (pl.col("wavelength_nm") <= 700)
)

# Summarize by spin multiplicity
by_mult = abs_spec.group_by("mult").agg([
    pl.count(),
    pl.mean("energy_ev").alias("avg_energy"),
    pl.max("osc_strength").alias("max_intensity")
])
```

## Data Structure

Blackfish uses [Polars](https://pola.rs/) DataFrames for efficient data handling. Common DataFrame schemas include:

### IR Spectrum
- `mode`: Vibrational mode number
- `frequency_cm`: Frequency in cm⁻¹
- `intensity`: IR intensity
- `rel_intensity`: Normalized intensity
- `tx/ty/tz`: Transition dipole components

### Excited States (Roots)
- `root`: State number
- `mult`: Spin multiplicity
- `donor`: Donor orbital
- `acceptor`: Acceptor orbital
- `weight`: Configuration weight
- `energy_cm`: Energy in cm⁻¹

### SOC States
- `state`: SOC state number
- `spin`: Spin component
- `root`: Contributing root state
- `weight`: State contribution weight
- `energy_cm`: Energy in cm⁻¹

### NACME
- `id`: Atom index
- `symbol`: Atomic symbol
- `x/y/z`: Coupling vector components
- `magnitude`: Total coupling magnitude

### SOC Absorption Spectrum
- `state`: Final state number
- `mult`: State multiplicity
- `energy_ev`: Transition energy in eV
- `energy_cm`: Energy in cm⁻¹
- `wavelength_nm`: Wavelength in nm
- `osc_strength`: Oscillator strength
- `rel_intensity`: Normalized intensity

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache2.0 License - see the LICENSE file for details.
