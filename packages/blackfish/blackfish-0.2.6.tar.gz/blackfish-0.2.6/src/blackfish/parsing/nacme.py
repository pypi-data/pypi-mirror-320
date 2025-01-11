from pathlib import Path

import polars as pl

from .utils import find_table_starts


def nacme(orca_output: Path) -> pl.DataFrame:
    """
    Extract non-adiabatic coupling matrix elements from an ORCA output file.

    Args:
        orca_output (Path): Path to the ORCA output file.

    Returns:
        pl.DataFrame: A DataFrame containing the NAC vectors between electronic states
            with columns 'id', 'symbol', 'x', 'y', 'z', and 'magnitude'.
            id - atom index
            symbol - atomic symbol
            x,y,z - NAC vector components
            magnitude - sum of absolute values of vector components
    """
    lines = Path(orca_output).read_text().splitlines()

    TABLE_HEADER = "CARTESIAN NON-ADIABATIC COUPLINGS"
    TABLE_HEADER_OFFSET = 5

    table_start_idx = next(find_table_starts(lines, TABLE_HEADER, TABLE_HEADER_OFFSET))

    # Collect table
    rows = []
    for row in lines[table_start_idx:]:
        # Stop on empty line
        if not row.strip():
            break

        rows.append(row.split())

    df = pl.DataFrame(
        rows,
        schema={"id": int, "symbol": str, "_": str, "x": float, "y": float, "z": float},
        orient="row",
    ).drop("_")

    # Compute magnitude
    df = df.with_columns(
        (pl.col("x").abs() + pl.col("y").abs() + pl.col("z").abs()).alias("magnitude")
    )

    return df
