from pathlib import Path


class Instructions:
    def __init__(self, settings: dict) -> None:
        self.settings = settings

        self.grid_size = settings.get("grid_size", 100)
        self.ids = settings.get("ids", [])
        self.plot_type = settings.get("plot_type", "orbital")
        self.triplet_root = settings.get("triplet_root", False)
        self.orbital_file = settings.get("orbital_file", None)
        self.triplet_root = settings.get("triplet_root", False)
        self.tda = settings.get("tda", True)
        self.nroots = settings.get("nroots", 0)

    def compile(self) -> str:
        instructions = ""
        instructions += Instructions.set_grid_size(self.grid_size)
        match self.plot_type:
            case "orbital":
                for id in self.ids:
                    instructions += Instructions.generate_orbital_plot(id)
                instructions += Instructions.exit()
            case "diffdens":
                # Adjust for whether TDA is False and triplet roots are requested
                ids = self.ids
                nroots = self.nroots
                if self.tda is False:
                    ids = [(id * 2) - 1 for id in ids]
                    nroots *= 2
                if self.triplet_root:
                    ids = [id + nroots for id in ids]

                for id in ids:
                    instructions += Instructions.generate_difference_density(
                        id, self.orbital_file
                    )
                instructions += Instructions.exit()
        return instructions

    @staticmethod
    def set_grid_size(grid_size: int = 100) -> str:
        return f"4\n{grid_size}\n"

    @staticmethod
    def generate_difference_density(id: str, orbital_file: Path) -> str:
        return f"6\nn\n{orbital_file.with_suffix(".cis")}\n{id}\n"

    @staticmethod
    def generate_orbital_plot(id: int) -> str:
        return f"2\n{id}\n11\n"

    @staticmethod
    def exit() -> str:
        return "12\n"
