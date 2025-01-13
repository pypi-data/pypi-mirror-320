CPT_QC_MAX = 20.0  # for the cpt plots
CPT_FR_MAX = 10.0  # for the cpt plots and limiting fr if qc <= 0.0
DEFAULT_CPT_INTERPRETATION_MIN_LAYERHEIGHT = (
    0.1  # minimum layer height for cpt interpretations
)
DEFAULT_CPT_INTERPRETATION_PEAT_FRICTION_RATIO = 1e9  # default peat friction ratio (any measurement above this value will be interpreted as peat no matter the qc or fs)

BRO_CPT_DOWNLOAD_URL = "https://publiek.broservices.nl/sr/cpt/v1/objects"
BRO_CPT_CHARACTERISTICS_URL = (
    f"https://publiek.broservices.nl/sr/cpt/v1/characteristics/searches"
)
UNIT_WEIGHT_WATER = 9.81
DEFAULT_LOAD_CONSOLIDATION = 10.0
DEFAULT_LOAD_SPREAD = 30.0
DEFAULT_TREE_WIDTH_ROOTZONE = 5.0
DEFAULT_TREE_DEPTH_EXCAVATION = 1.0
QCMAX_PEAT = 1.0  # if we use a friction ratio for peat we check two things, is fr >= the given friction ratio AND is qc < QCMAX peat

MIN_GEOM_SIZE = 0.01  # the minimum area size (in m2) for a fill layer to be added, smaller layers will be skipped to avoid strange geometries

DEFAULT_VOXELS_FROM_CPT_BORDER = 10  # use a 10m offset from the border found around the given cpts in the Voxel.from_cpts method
DEFAULT_VOXEL_XY_RESOLUTION = 10  # default size of a voxel in world coords (meters)
DEFAULT_VOXEL_Z_RESOLUTION = 0.5  # default size of a voxel in depth (meters)
DEFAULT_VOXEL_MAX_CPT_DISTANCE = 10  # any voxel closer to a cpt than this distance will get assigned to the voxel model
DEFAULT_VOXEL_MAX_POLYLINE_DISTANCE = 30  # any voxel further from the polyline than this value will have no soil properties
DEFAULT_VOXEL_APPLY_INTERPOLATION = False
