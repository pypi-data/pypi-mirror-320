from molSimplify.Classes.atom3D import atom3D


class TransitionMetal:
    """Class to represent a transition metal atom.

    Holds information about the atom, its oxidation state, number of electrons, multiplicities, and number of roots.
    """

    TRANSITION_METAL_GROUPS = {
        "sc": 1,
        "ti": 2,
        "v": 3,
        "cr": 4,
        "mn": 5,
        "fe": 6,
        "co": 7,
        "ni": 8,
        "cu": 9,
        "zn": 10,
        "y": 1,
        "zr": 2,
        "nb": 3,
        "mo": 4,
        "tc": 5,
        "ru": 6,
        "rh": 7,
        "pd": 8,
        "ag": 9,
        "cd": 10,
        "la": 1,
        "hf": 2,
        "ta": 3,
        "w": 4,
        "re": 5,
        "os": 6,
        "ir": 7,
        "pt": 8,
        "au": 9,
        "hg": 10,
    }

    POSSIBLE_ELECTRON_CONFIGURATIONS = {
        1: {2: 5},
        2: {3: 10, 1: 15},
        3: {4: 10, 2: 40},
        4: {5: 5, 3: 45, 1: 50},
        5: {6: 1, 4: 24, 2: 75},
        6: {5: 5, 3: 45, 1: 50},  # same as 4
        7: {4: 10, 2: 40},  # same as 3
        8: {3: 10, 1: 15},  # same as 2
        9: {2: 5},  # same as 1
    }

    def __init__(self, atom: atom3D, ox_state: int) -> None:
        self.atom = atom
        self.ox_state = ox_state
        self.n_electrons = self.get_n_electrons(self.atom.symbol(), ox_state)
        self.mults = self.get_mults(self.n_electrons)
        self.nroots = [self.get_nroots(self.n_electrons, mult) for mult in self.mults]

    def to_dict(self) -> dict:
        data = {
            "symbol": self.atom.symbol(),
            "coords": self.atom.coords(),
            "ox_state": self.ox_state,
            "n_electrons": self.n_electrons,
            "mults": self.mults,
            "nroots": self.nroots,
        }
        return dict(sorted(data.items()))

    @staticmethod
    def get_n_electrons(symbol: str, ox_state: int) -> int:
        return (TransitionMetal.TRANSITION_METAL_GROUPS[symbol.lower()] + 2) - ox_state

    @staticmethod
    def get_mults(n_electrons: int) -> list[int]:
        return list(
            TransitionMetal.POSSIBLE_ELECTRON_CONFIGURATIONS[n_electrons].keys()
        )

    @staticmethod
    def get_nroots(n_electrons: int, mult: int) -> int:
        return TransitionMetal.POSSIBLE_ELECTRON_CONFIGURATIONS[n_electrons][mult]
