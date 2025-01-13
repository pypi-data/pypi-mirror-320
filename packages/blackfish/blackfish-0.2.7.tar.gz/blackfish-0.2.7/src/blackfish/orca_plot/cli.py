import sys
from pathlib import Path

import click

from blackfish.orca_plot.engine import OrcaPlotEngine
from blackfish.orca_plot.instructions import Instructions


def plot(instructions: str, file: Path):
    engine = OrcaPlotEngine()
    engine.plot(instructions, file)


def parse_range(ctx, param, value) -> set:
    """Parse a range or individual numbers into a set."""
    numbers = []
    for item in value:
        try:
            if "-" in item:
                start, end = map(int, item.split("-"))
                numbers.extend(range(start, end + 1))  # Include end of range
            else:
                numbers.append(int(item))
        except ValueError:
            click.echo(
                f"Failed to parse: `{item}`. Use `-f/--file` to specify a .gbw file.",
                err=True,
            )
            sys.exit(1)
    return set(numbers)


def parse_value_from_file(file: Path, key: str) -> str | None:
    for line in file.read_text().splitlines():
        tokens = line.lower().split()
        for i, token in enumerate(tokens):
            if token == key.lower():
                return tokens[i + 1]
    return None


def get_orbital_file_in_cwd() -> Path | None:
    orbital_files_in_cwd = list(Path(".").glob("*.gbw"))
    match len(orbital_files_in_cwd):
        case 0:
            return None
        case 1:
            return orbital_files_in_cwd[0]
        case _:
            click.echo("Multiple .gbw files found in the current directory.")
            click.echo("Please specify the file to use with the `-f/--file` option.")
    return None


@click.command()
@click.option(
    "-g", "--grid-size", type=int, default=100, help="Grid size for the plot."
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Specify .gbw file to use. Defaults to the only .gbw file in the current directory.",
)
@click.option("-d", "--diffdens", is_flag=True, help="Plot difference densities.")
@click.option(
    "-t",
    "--triplet-root",
    is_flag=True,
    help="Convert IDs to triplet roots.",
)
@click.argument("ids", nargs=-1, callback=parse_range)
def cli(grid_size, ids, diffdens, triplet_root, file):
    """
    Parse grid size and IDs for plotting.

    IDS: A list of integers or ranges (e.g., 1-4).
    """

    settings = {}

    plot_type = "diffdens" if diffdens else "orbital"
    click.echo(f"Plot Type: {plot_type.upper()}")
    settings.update({"plot_type": plot_type})

    click.echo(f"Grid Size: {grid_size}")
    settings.update({"grid_size": grid_size})

    click.echo(f"IDs: {ids}")
    settings.update({"ids": ids})

    click.echo(f"Plotting triplet roots: {triplet_root}")
    settings.update({"triplet_root": triplet_root})

    orbital_file = file or get_orbital_file_in_cwd()
    if not orbital_file:
        click.echo(
            "No .gbw file found in the current directory and none specified."
            "Use `-f/--file` to specify a .gbw file.",
            err=True,
        )
        sys.exit(1)
    click.echo(f"Orbital file: {orbital_file}")
    settings.update({"orbital_file": orbital_file})

    if plot_type == "diffdens":
        input_file = orbital_file.with_suffix(".inp")
        if not input_file.exists():
            click.echo(f"ORCA input file not found: {input_file}", err=True)
            sys.exit(1)
        tda = parse_value_from_file(input_file, "tda")
        tda = bool(tda) if tda else True
        settings.update({"tda": tda})
        click.echo(f"TDA: {settings['tda']}")

        nroots = parse_value_from_file(input_file, "nroots")
        nroots = int(nroots) if nroots else 0
        settings.update({"nroots": nroots})
        if plot_type == "diffdens":
            click.echo(f"Roots: {settings['nroots']}")

    # Translate the settings into instructions
    instructions = Instructions(settings).compile()
    plot(instructions, orbital_file)


if __name__ == "__main__":
    cli()
