from typing import Iterator

from blackfish.parsing.exceptions import ParsingError


def find_table_starts(lines: list[str], header: str, offset: int) -> Iterator[int]:
    """
    Find all starting indices of tables in ORCA output files.

    Args:
        lines: List of strings containing the file content
        header: The header text to search for
        offset: Number of lines to skip after the header

    Yields:
        int: Indices where table data starts

    Raises:
        ParsingError: If no headers are found in the file
    """
    found = False
    for i, line in enumerate(lines):
        if header in line.strip():
            found = True
            yield i + offset

    if not found:
        raise ParsingError(f"Could not find '{header}'")
