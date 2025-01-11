"""Compute the phosphorescence rate from a SOC-TDDFT calculation.

Adapted from https://codeberg.org/AKW/phosphorescence_lifetime

"Predicting Phosphorescence Rates of Light Organic Molecules Using Time-Dependent
Density Functional Theory and the Path Integral Approach to Dynamics"
B. de Souza, G. Farias, F. Neese and R. Izsák, J. Chem. Theory Comput., 2019, 15, 1896–1904.
DOI: 10.1021/acs.jctc.8b00841
"""

from typing import Optional

import polars as pl

from blackfish.energy_units import CONVERSION_TO_HARTREE


def calculate_phosp_rate(
    soc_spectrum: pl.DataFrame,
    temperature_k: float = 298.15,
    refractive_index: float = 1.0,
    number_of_states: Optional[int] = None,
) -> float:
    """
    Calculate the phosphorescence rate from SOC absorption spectrum DataFrame.

    Args:
        soc_spectrum (pl.DataFrame): DataFrame containing a SOC spectrum.
        temperature_k (float, optional): Temperature in Kelvin for the Boltzmann distribution. Defaults to 298.15 K.
        refractive_index (float, optional): Refractive index of the solvent. Defaults to 1.0.
        number_of_states (Optional[int], optional): Number of excited states to include.
            Defaults to None, which includes all states with a normalized Boltzmann-weight >= 0.1%.

    Returns:
        float: Overall phosphorescence rate in [1/s].
    """
    # Constants in atomic units (au)
    speed_of_light = 137.035999
    femtosecond = 41.3413745758
    t_0 = 1
    alpha_0 = 1 / speed_of_light
    k_B = 3.166811563e-6  # hartree / K

    # Step 1: Convert energy from 1/cm to Hartree
    df = soc_spectrum.with_columns(
        (pl.col("energy_cm") * CONVERSION_TO_HARTREE["1/cm"]).alias("Energy [Eh]")
    )

    # Step 2: Compute Transition Dipole Moment (TDM) from t2
    df = df.with_columns((pl.col("d2").sqrt()).alias("TDM"))

    # Step 3: Calculate phosphorescence rate for each substate
    df = df.with_columns(
        [
            (
                (4 / 3 / t_0)
                * (alpha_0**3)
                * (pl.col("Energy [Eh]") ** 3)
                * (pl.col("TDM") ** 2)
                * pl.lit(femtosecond)
                * pl.lit(1e15)
                * pl.lit(refractive_index**2)
            ).alias("Phosp. Rate [1/s]")
        ]
    )

    # Step 5: Calculate ΔE [Eh] relative to the lowest energy excited state
    min_energy = df["Energy [Eh]"].min()
    df = df.with_columns((pl.col("Energy [Eh]") - min_energy).alias("ΔE [Eh]"))

    # Step 6: Calculate Boltzmann factors
    df = df.with_columns(
        (-pl.col("ΔE [Eh]") / (k_B * temperature_k)).exp().alias("Weight")
    )

    # Step 7: Normalize the weights
    sum_weights = df["Weight"].sum()
    df = df.with_columns((pl.col("Weight") / sum_weights).alias("Weight"))

    # Step 8: Exclude states where ΔE [Eh] <= 0 to avoid division by zero
    # TODO Should this raise an error?
    #  If there are states where ΔE [Eh] <= 0, the calculation is most likely invalid, right?
    df = df.filter((pl.col("ΔE [Eh]") > 0) & (pl.col("Phosp. Rate [1/s]") > 0))

    # Step 9: Decide how many excited states to include
    if number_of_states:
        # Select the top 'number_of_states' states based on energy
        selected_df = df.sort("Energy [Eh]", descending=False).head(number_of_states)
    else:
        # Include all states with a normalized weight >= 0.01%
        cutoff = 1e-4  # 0.01%
        selected_df = df.filter(pl.col("Weight") >= cutoff)

    # Step 10: Compute the overall phosphorescence rate as a weighted sum
    overall_phosphorescence_rate = (
        selected_df["Phosp. Rate [1/s]"] * selected_df["Weight"]
    ).sum()

    return overall_phosphorescence_rate


def calculate_phosp_lifetime(
    soc_spectrum: pl.DataFrame,
    temperature_k: float = 298.15,
    refractive_index: float = 1.0,
    number_of_states: Optional[int] = None,
) -> float:
    """
    Calculate the phosphorescence lifetime from SOC absorption spectrum DataFrame.

    Args:
        soc_spectrum (pl.DataFrame): DataFrame containing a SOC spectrum.
        temperature_k (float, optional): Temperature in Kelvin for the Boltzmann distribution. Defaults to 298.15 K.
        refractive_index (float, optional): Refractive index of the solvent. Defaults to 1.0.
        number_of_states (Optional[int], optional): Number of excited states to include.
            Defaults to None, which includes all states with a normalized Boltzmann-weight >= 0.1%.

    Returns:
        float: Overall phosphorescence lifetime in [s].
    """
    rate = calculate_phosp_rate(
        soc_spectrum, temperature_k, refractive_index, number_of_states
    )
    if rate == 0:
        return float("inf")
    return 1 / rate
