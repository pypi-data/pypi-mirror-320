import numpy as np
import matplotlib.pyplot as plt
from ..pubmeth import PubMethod
from ..filesop.filesave import FilesSave


class TriLats:
    def __init__(
        self,
        a1: np.ndarray,
        a2: np.ndarray,
        density_tuple: tuple = (15, 15),
        shift_arr: np.ndarray = np.array([0, 0]),
    ) -> None:
        self.a1 = a1
        self.a2 = a2
        self.shift_arr = shift_arr

        self.density_tuple = density_tuple

    @property
    def points(self) -> np.ndarray:
        xm, ym = np.meshgrid(
            np.arange(-self.density_tuple[0], self.density_tuple[0]),
            np.arange(-self.density_tuple[1], self.density_tuple[1]),
        )
        xm = xm.reshape((-1, 1))
        ym = ym.reshape((-1, 1))
        return xm * self.a1 + ym * self.a2 + self.shift_arr

    def __getitem__(self, key):
        return self.points[key]


class HexLats:
    def __init__(
        self,
        a1: np.ndarray,
        a2: np.ndarray,
        density_tuple: tuple = (15, 15),
        r_angle=0,
        shift_arr: np.ndarray | tuple[float, float] = np.array([0, 0]),
        z_shift: float | None = 0,
    ) -> None:
        """init function for hexagonal lattices

        Args:
            r_angle (rotation angle, unit of degree): float
            a1: lattices
            a2: lattice vectors
            density_tuple: density of the dots along two basis vectors.
            shift_arr: in-plane shifts
            z_shift: z-direction shift
        """
        self.a1 = a1
        self.a2 = a2
        self.density_tuple = density_tuple

        self.r_angle = r_angle
        self.shift_arr = shift_arr

        self.z_shift = z_shift

        if a1 @ a2 < 0:
            self.d_arr = (a1 - a2) / 3
        elif a1 @ a2 > 0:
            self.d_arr = (a1 + a2) / 3

    @property
    def lat1(self):
        return TriLats(self.a1, self.a2, self.density_tuple)

    @property
    def lat2(self):
        return TriLats(self.a1, self.a2, self.density_tuple, shift_arr=self.d_arr)

    @property
    def fInst(self):
        return FilesSave("Plot/HexLats")

    @property
    def _all_lats(self) -> np.ndarray:
        all_lats = (
            np.transpose(
                PubMethod.r_mat(self.r_angle)
                @ np.vstack([self.lat1[:], self.lat2[:]]).T
            )
            + self.shift_arr
        )
        if self.z_shift is not None:
            z_arr = np.ones((len(all_lats), 1)) * self.z_shift
            all_lats = np.hstack([all_lats, z_arr])

        return all_lats

    @_all_lats.setter
    def _all_lats(self, condition) -> np.ndarray:
        return self._all_lats[condition]

    def __getitem__(self, key):
        return self._all_lats[key]

    def __repr__(self) -> str:
        return str(self[:])

    def __add__(self, arrs: np.ndarray):
        if len(arrs.shape) < 2:
            if arrs.shape[0] == self[:].shape[1]:
                return self[:] + np.kron(np.ones((len(self[:]), 1)), arrs)
            else:
                raise TypeError(
                    "Two arrs must at least have the same columns. The Shape of two array is ",
                    arrs.shape,
                    self[:].shape,
                )

        elif len(arrs.shape) == 2:
            if arrs.shape == self[:].shape:
                return self[:] + arrs
            else:
                raise TypeError(
                    "Two arrs must have the same shape. The Shape of two array is ",
                    arrs.shape,
                    self[:].shape,
                )

    def __sub__(self, arrs: np.ndarray):
        return self.__add__(-arrs)

    def basis_change(self, r1: np.ndarray, r2: np.ndarray):
        """Change the coordinates of points based on the given r1, r2

        Args:
            r1: vectors of new basis
            r2: vectors of new basis

        Returns:
            arrays of the points in the new basis: np.ndarray
        """
        inv_mat = np.linalg.inv(
            np.array(
                [
                    [np.linalg.norm(r1) ** 2, r1 @ r2],
                    [r1 @ r2, np.linalg.norm(r1) ** 2],
                ]
            )
        )

        lats: np.ndarray = self[:][:, :2] @ np.hstack(
            [r1.reshape((-1, 1)), r2.reshape((-1, 1))]
        )

        return np.transpose(inv_mat @ lats.T)

    def plot(self, fig_name="hex_lattices"):
        """
        Plot points distributions
        """
        points = self[:]
        fig, ax = plt.subplots()
        ax.scatter(points[:, 0], points[:, 1], marker=".", s=0.6, c="r")
        ax.set_aspect("equal")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Distribution of hexagon lattices")
        self.fInst.save_fig(fig, fig_name)
        plt.close(fig)
