from pathlib import Path

import polars as pl

from .utils import find_table_starts


def ir_spectrum(orca_output: Path) -> pl.DataFrame:
    """
    Parse IR spectrum data from ORCA output file.

    Args:
        orca_output (Path): Path to ORCA output file containing IR spectrum data

    Returns:
        pl.DataFrame: DataFrame containing IR spectral data with columns:
            - mode: Mode number
            - frequency_cm: Frequency in cm^-1
            - epsilon: Epsilon value
            - intensity: Raw intensity
            - t2: T2 value
            - tx: Tx value
            - ty: Ty value
            - tz: Tz value
            - rel_intensity: Intensity normalized to maximum value
    """
    lines = Path(orca_output).read_text().splitlines()

    TABLE_HEADER = "IR SPECTRUM"
    TABLE_HEADER_OFFSET = 6

    table_start_idx = next(find_table_starts(lines, TABLE_HEADER, TABLE_HEADER_OFFSET))

    # Collect table
    rows = []
    for row in lines[table_start_idx:]:
        # Stop on empty line
        if not row.strip():
            break

        rows.append(row)

    processed_rows = [
        row.replace(":", "").replace("(", "").replace(")", "").strip().split()
        for row in rows
    ]

    df = pl.DataFrame(
        processed_rows,
        orient="row",
        schema={
            "mode": pl.Int64,
            "frequency_cm": pl.Float64,
            "epsilon": pl.Float64,
            "intensity": pl.Float64,
            "t2": pl.Float64,
            "tx": pl.Float64,
            "ty": pl.Float64,
            "tz": pl.Float64,
        },
    )

    df = df.with_columns(
        (pl.col("intensity") / pl.col("intensity").max()).alias("rel_intensity")
    )

    return df
