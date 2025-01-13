from pydantic import BaseModel, ConfigDict
from typing import List, Tuple, Dict
import numpy as np
import matplotlib.pyplot as plt
from math import hypot
from shapely.geometry import LineString, Point

from ..objects.cpt import Cpt, CptInterpretationMethod
from ..settings import (
    DEFAULT_VOXELS_FROM_CPT_BORDER,
    DEFAULT_CPT_INTERPRETATION_PEAT_FRICTION_RATIO,
    DEFAULT_VOXEL_XY_RESOLUTION,
    DEFAULT_VOXEL_Z_RESOLUTION,
    DEFAULT_VOXEL_MAX_CPT_DISTANCE,
    DEFAULT_VOXEL_APPLY_INTERPOLATION,
    DEFAULT_VOXEL_MAX_POLYLINE_DISTANCE,
)
from ..objects.soilcollection import SoilCollection


def compute_min_distances(Mxy, polyline_coords):
    """
    Compute the minimum distance from each point in a structured grid (Mxy) to a polyline.

    Parameters:
    - Mxy: 3D numpy array of shape (Nx, Ny, 2), where each entry contains (x, y) coordinates.
    - polyline_coords: List of (x, y) tuples defining the polyline.

    Returns:
    - distance_matrix: 2D numpy array of shape (Nx, Ny) containing minimal distances.
    """
    polyline = LineString(polyline_coords)  # Convert polyline to a Shapely LineString

    # Extract Nx, Ny dimensions
    Nx, Ny, _ = Mxy.shape

    # Flatten Mxy into a list of (x, y) coordinates
    points = Mxy.reshape(-1, 2)

    # Compute distances vectorized
    distances = np.array([polyline.distance(Point(p)) for p in points])

    # Reshape back to the grid shape (Nx, Ny)
    return distances.reshape(Nx, Ny)


class VoxelModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    xmin: float = 0.0
    ymin: float = 0.0
    xmax: float = 0.0
    ymax: float = 0.0
    zmin: float = 0.0
    zmax: float = 0.0
    xy_resolution: float = 10
    z_resolution: float = 0.5
    M: np.ndarray = None
    soilcodes: Dict = {}

    @classmethod
    def from_cpts(
        cls,
        polyline: List[Tuple[float, float]],
        cpts: List[Cpt],
        peat_friction_ratio: float = DEFAULT_CPT_INTERPRETATION_PEAT_FRICTION_RATIO,
        margin: float = DEFAULT_VOXELS_FROM_CPT_BORDER,
        xy_resolution: float = DEFAULT_VOXEL_XY_RESOLUTION,
        z_resolution: float = DEFAULT_VOXEL_Z_RESOLUTION,
        max_cpt_distance: float = DEFAULT_VOXEL_MAX_CPT_DISTANCE,
        max_polyline_distance: float = DEFAULT_VOXEL_MAX_POLYLINE_DISTANCE,
        apply_interpolation: bool = DEFAULT_VOXEL_APPLY_INTERPOLATION,
    ):
        # TODO
        # toevoegen filter op max afstand van polyline
        # die punten hoeven dan ook niet door het interpolatie proces
        # en maakt het weer sneller
        # actie maak 2D matrix

        # per punt bereken de korste afstand naar de polyline
        # filter alle > max_polyline_distance en zet op -1
        # gebruik die info bij het x,y,z doorlopen en skip -1 entries

        result = VoxelModel(xy_resolution=xy_resolution, z_resolution=z_resolution)

        xs = [p[0] for p in polyline]
        ys = [p[1] for p in polyline]

        xmin = min(xs) - margin
        ymin = min(ys) - margin
        xmax = max(xs) + margin
        ymax = max(ys) + margin

        nx = int((xmax - xmin) / result.xy_resolution) + 1
        ny = int((ymax - ymin) / result.xy_resolution) + 1

        result.xmin = xmin
        result.ymin = ymin
        result.xmax = xmin + nx * result.xy_resolution
        result.ymax = ymin + ny * result.xy_resolution

        # create an array of xy locations in the grid
        Ax = np.arange(result.xmin, result.xmax, xy_resolution)
        Ay = np.arange(result.ymin, result.ymax, xy_resolution)
        Ax += xy_resolution / 2.0
        Ay += xy_resolution / 2.0
        X, Y = np.meshgrid(Ax, Ay, indexing="ij")
        Mxy = np.stack((X, Y), axis=2)

        # create a matrix of distances from voxel to polyline
        distance_matrix = compute_min_distances(Mxy, polyline)
        # set those too far away from the polyline to -1
        distance_matrix[distance_matrix > max_polyline_distance] = -1

        soilprofiles = {}
        soilcodes = []
        zmin, zmax = 1e9, -1e9
        for cpt in cpts:  # TODO waarschuwing dat cpts unieke namen moeten hebben
            soilprofiles[cpt.name] = cpt.to_soilprofile(
                cpt_interpretation_method=CptInterpretationMethod.ROBERTSON,
                minimum_layerheight=z_resolution,
                peat_friction_ratio=peat_friction_ratio,
            )
            for sl in soilprofiles[cpt.name].soillayers:
                soilcodes.append(sl.soilcode)
            zmin = min(zmin, soilprofiles[cpt.name].bottom)
            zmax = max(zmax, soilprofiles[cpt.name].top)

        # get unique soilnames
        soilcodes = set(list(soilcodes))

        # convert to dict with id (starting with 1 because 0 = no soil)
        for i, soilcode in enumerate(soilcodes):
            result.soilcodes[soilcode] = i + 1

        nz = int((zmax - zmin) / z_resolution) + 1
        result.zmax = zmax
        result.zmin = zmax - nz * result.z_resolution
        result.M = np.zeros((nx, ny, nz))

        # create z matrix for every cpt
        Mcpts = {}
        for cpt_name, soilprofile in soilprofiles.items():
            Mcpts[cpt_name] = np.zeros(nz, dtype=np.uint8)
            for i in range(nz):
                soillayer = soilprofile.soillayer_at_z(zmax - (i + 0.5) * z_resolution)
                if soillayer is None:
                    Mcpts[cpt_name][i] = 0
                else:
                    Mcpts[cpt_name][i] = result.soilcodes[soillayer.soilcode]

        if apply_interpolation:
            # create a 2D matrix per cpt that contains the distance to the cpt from the centre of the matrix element
            Mcptdl = {}
            for cpt in cpts:
                cpt_x, cpt_y = cpt.x, cpt.y
                distances = np.linalg.norm(Mxy - np.array([cpt_x, cpt_y]), axis=2)
                # apply the max distance filter
                distances[distances > max_cpt_distance] = -1
                # convert to weights
                # avoid div 0
                distances[distances == 0] = 1e-2
                distances = 1 / (distances / max_cpt_distance)
                # reset the invalid ones to -1
                distances[distances < 0] = -1
                Mcptdl[cpt.name] = distances

            # create the recipe per element
            # a recipe contains the cpts within max_cpt_distance and a weight
            # that represents a kind of distance based weight (higher = closer)
            # a recipe can contain multiple cpts and weights
            Mrecipes = {}
            for x in range(nx):
                for y in range(ny):
                    if distance_matrix[x][y] == -1:
                        continue
                    recipe = ""
                    for cpt in cpts:
                        if Mcptdl[cpt.name][x][y] > -1:
                            recipe += f"{cpt.name},{Mcptdl[cpt.name][x][y]:.1f},"

                    if recipe != "":
                        Mrecipes[f"{x},{y}"] = recipe[:-1]  # remove the last comma

            # per location find the likely soiltype
            # we use the recipe to find the soiltype per cpt
            # and sums the weights if we have multiple cpts
            # finally we assign the soiltype with the highest weight
            for x in range(nx):
                for y in range(ny):
                    if distance_matrix[x][y] == -1:
                        continue
                    k = f"{x},{y}"
                    if k in Mrecipes.keys():
                        recipe = Mrecipes[k].split(
                            ","
                        )  # TODO dit betekent geen komma in de cpt naam!
                        cpt_names = recipe[::2]
                        weights = [float(s) for s in recipe[1::2]]
                        for z in range(nz):
                            # get the soil at this location (in Mcpts)
                            weights_dict = {}
                            for cpt_name, w in zip(cpt_names, weights):
                                soilcode = Mcpts[cpt_name][z]
                                weights_dict[soilcode] = (
                                    weights_dict.get(soilcode, 0) + w
                                )

                            max_soilcode = max(weights_dict, key=weights_dict.get)
                            result.M[x][y][z] = int(max_soilcode)
        else:
            # simply assing the closest CPT
            for x in range(nx):
                for y in range(ny):
                    if distance_matrix[x][y] == -1:
                        continue
                    xc = result.nx_to_x(x)
                    yc = result.ny_to_y(y)
                    dlmin = 1e9
                    closest_cpt = None
                    for cpt in cpts:
                        dl = hypot(cpt.x - xc, cpt.y - yc)
                        if dl <= dlmin and dl < max_cpt_distance:
                            dlmin = dl
                            closest_cpt = cpt
                    if closest_cpt is not None:
                        result.M[x][y] = Mcpts[closest_cpt.name]

        return result

    def nx_to_x(self, nx: int) -> float:
        return self.xmin + (nx + 0.5) * self.xy_resolution

    def ny_to_y(self, ny: int) -> float:
        return self.ymin + (ny + 0.5) * self.xy_resolution

    def nz_to_z(self, nz: int) -> float:
        return self.zmax - (nz + 0.5) * self.z_resolution

    def x_to_nx(self, x: float) -> int:
        return int((x - self.xmin) / self.xy_resolution)

    def y_to_ny(self, y: float) -> int:
        return int((y - self.ymin) / self.xy_resolution)

    def z_to_nz(self, z: float) -> int:
        return int((self.zmax - z) / self.z_resolution)

    def plot(self, soilcolors: Dict = None):
        color_map = {}

        sc = SoilCollection()
        scd = sc.get_color_dict()
        for k in self.soilcodes.keys():
            color_map[self.soilcodes[k]] = scd[k]

        mask = self.M > 0
        colors = np.empty(self.M.shape, dtype=object)
        for value, color in color_map.items():
            colors[self.M == value] = color

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection="3d")
        ax.voxels(mask, facecolors=colors, edgecolors="k", linewidth=0.5)

        x_size, y_size, _ = self.M.shape
        max_range = max(x_size, y_size)
        ax.set_xlim([0, max_range])
        ax.set_ylim([0, max_range])

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("3D Voxel Plot")

        plt.show()
