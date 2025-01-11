# energy_units.py

"""
Energy Units Conversion Module

This module provides functionality to convert energy values between different
quantum chemical units such as Hartree, eV, cm^-1, and kcal/mol.

Supported Units:
- hartree
- eV
- cm-1
- kcal/mol

Usage:
    from energy_units import convert_energy

    energy_in_ev = convert_energy(1.0, from_unit='hartree', to_unit='eV')
    print(f"1 Hartree is {energy_in_ev} eV")
"""

# Define conversion factors to Hartree
# 1 unit = factor * Hartree
CONVERSION_TO_HARTREE = {
    "hartree": 1.0,
    "ev": 1.0 / 27.211386245988,  # 1 eV ≈ 0.0367493 Hartree
    "1/cm": 1.0 / 219474.6313705,  # 1 cm^-1 ≈ 4.5563353e-6 Hartree
    "kcal/mol": 1.0 / 627.509474,  # 1 kcal/mol ≈ 0.0015936 Hartree
    "kj/mol": 1.0 / 2625.499638,  # 1 kJ/mol ≈ 0.0003809 Hartree
}

# List of supported units for easy reference
SUPPORTED_UNITS = list(CONVERSION_TO_HARTREE.keys())


def convert_energy(value, from_unit, to_unit):
    """
    Convert energy from one unit to another.

    Parameters:
        value (float): The numerical value of the energy to convert.
        from_unit (str): The unit of the input energy. Supported units:
                         'hartree', 'eV', 'cm-1', 'kcal/mol'
        to_unit (str): The unit to convert the energy into. Supported units:
                       'hartree', 'eV', 'cm-1', 'kcal/mol'

    Returns:
        float: The converted energy value in the desired unit.

    Raises:
        ValueError: If either from_unit or to_unit is not supported.
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit not in CONVERSION_TO_HARTREE:
        raise ValueError(
            f"Unsupported 'from_unit': {from_unit}. Supported units: {SUPPORTED_UNITS}"
        )

    if to_unit not in CONVERSION_TO_HARTREE:
        raise ValueError(
            f"Unsupported 'to_unit': {to_unit}. Supported units: {SUPPORTED_UNITS}"
        )

    # Convert the input value to Hartree
    value_in_hartree = value * CONVERSION_TO_HARTREE[from_unit]

    # Convert from Hartree to the desired unit
    converted_value = value_in_hartree / CONVERSION_TO_HARTREE[to_unit]

    return converted_value
