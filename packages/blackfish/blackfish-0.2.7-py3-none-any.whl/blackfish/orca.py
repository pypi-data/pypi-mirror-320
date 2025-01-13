from pathlib import Path

import altair as alt
import polars as pl

from blackfish.charts import soc_absorption_spectrum_chart
from blackfish.parsing import (
    Energies,
    ir_spectrum,
    nacme,
    roots,
    soc_absorption_spectrum,
    soc_states,
    socme,
)
from blackfish.structure import Structure


class ORCA:
    """Main class for parsing and analyzing ORCA quantum chemistry output files.

    Args:
        output_file: Path to ORCA output file
    """

    def __init__(self, output_file: Path):
        self.output_file = Path(output_file)
        assert (
            self.output_file.exists()
        ), f"Specified path not found: {self.output_file}"
        if self.output_file.is_dir():
            self.output_file = next(self.output_file.glob("*.out"))

    @property
    def ir_spectrum(self) -> pl.DataFrame:
        """Get IR spectrum data from ORCA output.

        Returns:
            DataFrame containing vibrational mode data with columns:
            mode, frequency_cm, intensity, rel_intensity, tx, ty, tz
        """
        return ir_spectrum(self.output_file)

    @property
    def nacme(self) -> pl.DataFrame:
        """Get non-adiabatic coupling matrix elements.

        Returns:
            DataFrame containing coupling vectors with columns:
            id, symbol, x, y, z, magnitude
        """
        return nacme(self.output_file)

    @property
    def roots(self) -> pl.DataFrame:
        """Get electronic excited state data.

        Returns:
            DataFrame containing state information with columns:
            root, mult, donor, acceptor, weight, energy_cm
        """
        return roots(self.output_file)

    @property
    def soc_absorption_spectrum(self) -> pl.DataFrame:
        """Get spin-orbit corrected absorption spectrum.

        Returns:
            DataFrame containing transition data with columns:
            state, mult, energy_ev, energy_cm, wavelength_nm,
            osc_strength, rel_intensity
        """
        return soc_absorption_spectrum(self.output_file)

    @property
    def soc_states(self) -> pl.DataFrame:
        """Get spin-orbit coupled states.

        Returns:
            DataFrame containing SOC state data with columns:
            state, spin, root, weight, energy_cm
        """
        return soc_states(self.output_file)

    def soc_absorption_spectrum_chart(self, **kwargs) -> alt.LayerChart:
        """Generate interactive plot of SOC absorption spectrum.

        Args:
            **kwargs: Keyword arguments passed to chart generation function.
                fwhm: Gaussian broadening width
                peaks: Whether to show peak markers
                peak_threshold: Minimum peak height to show
        """
        return soc_absorption_spectrum_chart(self.soc_absorption_spectrum, **kwargs)

    @property
    def energies(self):
        return Energies(self.output_file)

    @property
    def structure(self):
        return Structure.from_output_file(self.output_file)

    @property
    def socme(self) -> pl.DataFrame:
        """Get spin-orbit coupling matrix elements.

        Returns:
            DataFrame containing coupling vectors with columns:
            triplet_root, singlet_root, x, y, z, magnitude
        """
        return socme(self.output_file)
