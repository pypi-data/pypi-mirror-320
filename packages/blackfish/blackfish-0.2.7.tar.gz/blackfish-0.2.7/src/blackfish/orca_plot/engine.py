import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional


class OrcaPlotEngine:
    def __init__(self):
        pass

    def _get_executable(self):
        executable = shutil.which("orca_plot")
        if executable is None:
            raise FileNotFoundError("Failed to find `orca_plot` executable.")
        return Path(executable).resolve()

    def plot(self, instructions: str, file: Path, executable: Optional[Path] = None):
        if executable is None:
            executable = self._get_executable()
        with NamedTemporaryFile(mode="w+") as stdin:
            stdin.write(instructions.replace(" ", "\n"))
            stdin.seek(0)
            subprocess.run(
                [executable, file.resolve(), "-i"],
                stdin=stdin,
                stdout=subprocess.DEVNULL,
            )
