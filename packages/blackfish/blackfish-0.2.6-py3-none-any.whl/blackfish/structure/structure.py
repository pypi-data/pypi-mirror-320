from pathlib import Path
from typing import Self

import numpy as np
import plotly.graph_objects as go
import polars as pl

from blackfish.parsing.utils import find_table_starts
from blackfish.structure.elements import ELEMENTS


class Structure:
    """Class for handling Structure molecular coordinate files and data."""

    def __init__(self, atoms: pl.DataFrame) -> None:
        """Initialize Structure object with atomic coordinates.

        Args:
            atoms: DataFrame containing atomic coordinates with columns Symbol, X, Y, Z
        """
        self.df = atoms

    @classmethod
    def from_xyz_file(cls, file: Path) -> Self:
        """Create Structure object from an Structure file.

        Args:
            file: Path to Structure file

        Returns:
            New Structure instance
        """
        return cls(cls.parse_string(file.read_text()))

    @staticmethod
    def parse_string(string: str) -> pl.DataFrame:
        lines = string.splitlines()
        num_atoms = int(lines[0].strip())
        atoms = []
        for line in lines[2 : 2 + num_atoms]:
            parts = line.split()
            symbol = parts[0]
            x, y, z = map(float, parts[1:4])
            atoms.append({"Symbol": symbol, "X": x, "Y": y, "Z": z})
        return pl.DataFrame(atoms)

    @classmethod
    def from_str(cls, string: str) -> Self:
        """Create Structure object from an Structure string.

        Args:
            string: Structure string

        Returns:
            New Structure instance
        """
        return cls(cls.parse_string(string))

    def to_xyz_file(self, file: Path) -> None:
        """Write atomic coordinates to an Structure file.

        Args:
            file: Path where Structure file will be written
        """
        self.write_xyz_file(self.df, file)

    def write_xyz_file(self, atoms: pl.DataFrame, file: Path) -> None:
        """Write atomic coordinates DataFrame to an Structure file.

        Args:
            atoms: DataFrame containing atomic coordinates
            file: Path where Structure file will be written
        """
        file.write_text(self.to_string())

    def to_string(self) -> str:
        """Convert atomic coordinates to an Structure string.

        Returns:
            Structure string representation of atomic coordinates
        """
        return f"{len(self.df)}\n\n" + self.df.write_csv(
            include_header=False, separator=" "
        )

    @classmethod
    def from_output_file(cls, file: Path) -> Self:
        """Create Structure object from an ORCA output file.

        Args:
            file: Path to ORCA output file

        Returns:
            New Structure instance
        """
        return cls(cls.parse_output_file(file))

    @staticmethod
    def parse_output_file(file: Path) -> pl.DataFrame:
        """Parse atomic coordinates from an ORCA output file.

        Args:
            file: Path to ORCA output file

        Returns:
            DataFrame containing atomic coordinates from final geometry
        """
        lines = Path(file).read_text().splitlines()

        structures = []

        TABLE_HEADER = "CARTESIAN COORDINATES (ANGSTROEM)"
        TABLE_HEADER_OFFSET = 2

        for table_start in find_table_starts(lines, TABLE_HEADER, TABLE_HEADER_OFFSET):
            atoms = []
            for row in lines[table_start:]:
                if not row.strip():
                    break
                parts = row.split()
                symbol = parts[0]
                x, y, z = map(float, parts[1:4])
                atoms.append({"Symbol": symbol, "X": x, "Y": y, "Z": z})
            structures.append(pl.DataFrame(atoms))

        # Return the last structure, which is the final geometry for optimizations as well
        return pl.DataFrame(structures[-1])

    def detect_bonds(self, tolerance=1.2) -> list[tuple]:
        """Detect bonds between atoms based on covalent radii.

        Uses the sum of covalent radii multiplied by a tolerance factor to determine
        if atoms are bonded. Only considers atoms with radii defined in the covalent_radii
        dictionary.

        Args:
            tolerance: Multiplier for sum of covalent radii to determine bond cutoff

        Returns:
            List of tuples containing indices of bonded atom pairs
        """
        bonds = []
        num_atoms = len(self.df)
        symbols = self.df["Symbol"].to_list()
        xs = self.df["X"].to_list()
        ys = self.df["Y"].to_list()
        zs = self.df["Z"].to_list()

        for i in range(num_atoms):
            elem1 = symbols[i]
            if elem1 not in ELEMENTS:
                continue
            radius1 = ELEMENTS[elem1]["covalent_radius"]
            x1, y1, z1 = xs[i], ys[i], zs[i]
            for j in range(i + 1, num_atoms):
                elem2 = symbols[j]
                if elem2 not in ELEMENTS:
                    continue
                radius2 = ELEMENTS[elem2]["covalent_radius"]
                cutoff = (radius1 + radius2) * tolerance

                dx = x1 - xs[j]
                dy = y1 - ys[j]
                dz = z1 - zs[j]
                distance = np.sqrt(dx * dx + dy * dy + dz * dz)

                if distance <= cutoff:
                    bonds.append((i, j))
        return bonds

    def plot(self, width=640, height=320, title=None) -> go.Figure:
        bonds = self.detect_bonds()
        df = self.df.clone()

        # Decorate the df with color and size columns
        df = df.with_columns(
            pl.col("Symbol")
            .map_elements(lambda s: ELEMENTS[s]["color"], return_dtype=pl.Utf8)
            .alias("Color"),
            pl.col("Symbol")
            .map_elements(lambda s: ELEMENTS[s]["size"], return_dtype=pl.Float64)
            .alias("Size"),
        )

        # --- 1) Add the bond cylinders (re-using your custom method) ---
        # plot_bonds_as_cylinders(...) returns a figure with the cylinders added
        # but let's assume we can call it on the existing `fig` if you rewrite it slightly.
        # Or we can do it first and add to that figure.
        fig = self.plot_bonds_as_cylinders(bonds, ELEMENTS)

        # --- 2) Add the sphere for each atom ---
        # For each atom row in df:
        for idx in range(len(df)):
            x_atom = df["X"][idx]
            y_atom = df["Y"][idx]
            z_atom = df["Z"][idx]
            # Essentially "sticks" for H and C atoms
            match df["Symbol"][idx]:
                case "H":
                    radius_atom = 0.15
                case "C":
                    radius_atom = 0.25
                case _:
                    radius_atom = float(df["Size"][idx]) * 0.03
            color_atom = df["Color"][idx]

            # Build the sphere
            x_sphere, y_sphere, z_sphere, i_sphere, j_sphere, k_sphere = (
                self.create_sphere(
                    center=(x_atom, y_atom, z_atom),
                    radius=radius_atom,
                    n_steps=12,  # adjust for smoothness vs. performance
                )
            )

            fig.add_trace(
                go.Mesh3d(
                    x=x_sphere,
                    y=y_sphere,
                    z=z_sphere,
                    i=i_sphere,
                    j=j_sphere,
                    k=k_sphere,
                    color=color_atom,
                    opacity=1.0,
                    lighting=dict(
                        ambient=0.85,
                        diffuse=0.2,
                        specular=0.6,
                        roughness=0.5,
                        fresnel=0.5,
                    ),
                    name=f"Atom {idx}: {df['Symbol'][idx]}",
                    hoverinfo="skip",
                )
            )

        fig.update_layout(
            width=width,
            height=height,
            title=title,
            scene=dict(
                aspectmode="data",
                xaxis_visible=False,
                yaxis_visible=False,
                zaxis_visible=False,
                bgcolor="whitesmoke",
            ),
        )

        return fig

    def create_sphere(self, center, radius=1.0, n_steps=12):
        """
        Returns (x, y, z, i, j, k) for a Mesh3D sphere.
        center: (cx, cy, cz) in 3D
        radius: sphere radius
        n_steps: resolution (>= 4 recommended)
        """
        cx, cy, cz = center
        # Discretize polar angle theta (0 to pi)
        theta_vals = np.linspace(0, np.pi, n_steps + 1)
        # Discretize azimuth angle phi (0 to 2*pi)
        phi_vals = np.linspace(0, 2 * np.pi, n_steps, endpoint=False)

        # We'll build a 2D grid of shape (n_steps+1, n_steps).
        #  (theta index runs 0..n_steps, phi index runs 0..n_steps-1)
        # Then flatten to 1D arrays for x,y,z.

        # Each grid point is:
        #   x = cx + r sin(theta) cos(phi)
        #   y = cy + r sin(theta) sin(phi)
        #   z = cz + r cos(theta)

        # Use meshgrid for angles
        theta_grid, phi_grid = np.meshgrid(theta_vals, phi_vals, indexing="ij")

        # Compute x,y,z of all points
        x_2d = cx + radius * np.sin(theta_grid) * np.cos(phi_grid)
        y_2d = cy + radius * np.sin(theta_grid) * np.sin(phi_grid)
        z_2d = cz + radius * np.cos(theta_grid)

        # Flatten to 1D arrays
        x_all = x_2d.ravel()
        y_all = y_2d.ravel()
        z_all = z_2d.ravel()

        # Now build triangular faces by connecting adjacent grid cells:
        # For each cell in the domain i in [0..n_steps-1], j in [0..n_steps-1]:
        #   We have a 'square' in (theta,phi), which we split into two triangles.
        #   The flatten index of (theta_i, phi_j) in x_all is i*(n_steps) + j,
        #     because each row has n_steps entries.

        i_list = []
        j_list = []
        k_list = []

        # For convenience
        def idx(t, p):
            # clamp to valid range for wrapping phi in [0..n_steps-1]
            return t * (n_steps) + (p % n_steps)

        for t in range(n_steps):
            for p in range(n_steps):
                # 1) top-left triangle
                i0 = idx(t, p)
                i1 = idx(t, p + 1)
                i2 = idx(t + 1, p)
                # 2) bottom-right triangle
                i3 = idx(t + 1, p + 1)

                # Triangle #1
                i_list.append(i0)
                j_list.append(i1)
                k_list.append(i2)

                # Triangle #2
                i_list.append(i1)
                j_list.append(i3)
                k_list.append(i2)

        return x_all, y_all, z_all, i_list, j_list, k_list

    def create_cylinder(
        self,
        start_point,
        end_point,
        radius=0.05,  # Bond thickness
        n_segments=16,  # Resolution of the circular cross-section
        add_caps=True,  # Whether to close the cylinder ends
    ):
        """
        Returns (x, y, z, i, j, k) for a Mesh3D cylinder
        from start_point to end_point with given radius.
        """
        p0 = np.array(start_point, dtype=float)
        p1 = np.array(end_point, dtype=float)
        d = p1 - p0
        length = np.linalg.norm(d)
        if length < 1e-12:
            # Degenerate case: same start/end => small dummy cylinder
            return [p0[0]], [p0[1]], [p0[2]], [], [], []

        # Normalize direction
        d /= length

        # Find vector perpendicular to d
        # We'll pick 'up' as (0,0,1) unless d is already near that, in which case we pick (0,1,0).
        if abs(d[0]) < 1e-4 and abs(d[1]) < 1e-4:
            up = np.array([0, 1, 0], dtype=float)
        else:
            up = np.array([0, 0, 1], dtype=float)

        # Use cross products to get two perpendicular directions spanning the plane
        v = np.cross(d, up)
        v /= np.linalg.norm(v)
        w = np.cross(d, v)  # also perpendicular to d, v

        # Angles around the circular cross-section
        angles = np.linspace(0, 2.0 * np.pi, n_segments, endpoint=False)

        # Build bottom (p0) circle and top (p1) circle
        # shape: (3, n_segments)
        circle_bottom = (
            p0[:, None]
            + radius * np.cos(angles)[None, :] * v[:, None]
            + radius * np.sin(angles)[None, :] * w[:, None]
        )
        circle_top = (
            p1[:, None]
            + radius * np.cos(angles)[None, :] * v[:, None]
            + radius * np.sin(angles)[None, :] * w[:, None]
        )

        # Stack the vertices: first bottom ring, then top ring
        x = np.hstack([circle_bottom[0, :], circle_top[0, :]])
        y = np.hstack([circle_bottom[1, :], circle_top[1, :]])
        z = np.hstack([circle_bottom[2, :], circle_top[2, :]])

        # Build side faces (two triangles per side segment)
        i = []
        j = []
        k = []
        # For each segment in the bottom circle
        for seg in range(n_segments):
            # next index (with wrap-around)
            seg_next = (seg + 1) % n_segments

            # bottom index and top index
            b0 = seg
            b1 = seg_next
            t0 = seg + n_segments
            t1 = seg_next + n_segments

            # Two triangles for each rectangular side:
            # 1) b0 -> b1 -> t0
            i.extend([b0, b1])
            j.extend([b1, t0])
            k.extend([t0, b0])

            # 2) b1 -> t1 -> t0
            i.extend([b1])
            j.extend([t1])
            k.extend([t0])

        if add_caps:
            # Add center points for bottom and top
            bottom_center_idx = len(x)
            top_center_idx = len(x) + 1

            x = np.append(x, [p0[0], p1[0]])
            y = np.append(y, [p0[1], p1[1]])
            z = np.append(z, [p0[2], p1[2]])

            # Triangles for bottom cap
            for seg in range(n_segments):
                seg_next = (seg + 1) % n_segments
                i.append(bottom_center_idx)
                j.append(seg_next)
                k.append(seg)

            # Triangles for top cap
            for seg in range(n_segments):
                seg_next = (seg + 1) % n_segments
                i.append(top_center_idx)
                j.append(seg + n_segments)
                k.append(seg_next + n_segments)

        return x, y, z, i, j, k

    def plot_bonds_as_cylinders(self, bonds, ELEMENTS, BOND_SCALE=0.1):
        """
        df:       polars DataFrame (with columns: ["X","Y","Z","Symbol"])
        bonds:    list of (i, j) pairs from `self.detect_bonds()`
        ELEMENTS: dictionary with 'covalent_radius' etc.
        """
        df = self.df.clone()
        fig = go.Figure()

        for bond in bonds:
            i, j = bond

            # Atom positions
            x1, y1, z1 = df["X"][i], df["Y"][i], df["Z"][i]
            x2, y2, z2 = df["X"][j], df["Y"][j], df["Z"][j]

            # Create cylinder mesh for this bond
            (x_cyl, y_cyl, z_cyl, i_cyl, j_cyl, k_cyl) = self.create_cylinder(
                # start_point=(start_x, start_y, start_z),
                start_point=(x1, y1, z1),
                end_point=(x2, y2, z2),
                radius=0.12,  # tweak bond thickness as desired
                n_segments=16,
                add_caps=True,
            )

            fig.add_trace(
                go.Mesh3d(
                    x=x_cyl,
                    y=y_cyl,
                    z=z_cyl,
                    i=i_cyl,
                    j=j_cyl,
                    k=k_cyl,
                    color="gray",
                    opacity=1.0,
                    lighting=dict(
                        ambient=0.85,
                        diffuse=0.2,
                        specular=0.6,
                        roughness=0.5,
                        fresnel=0.5,
                    ),
                    flatshading=False,
                    name=f"bond_{i}_{j}",
                    hoverinfo="skip",
                )
            )

        # You can still add your atoms as scatter points or spheres here...
        # for example, as scatter3D or more complex mesh spheres

        fig.update_layout(scene=dict(aspectmode="data"))

        return fig
