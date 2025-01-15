import numpy as np
from simba.utils.checks import check_valid_array
from simba.utils.enums import Formats


def xie_beni_cuda(x: np.ndarray, y: np.ndarray) -> float:
    check_valid_array(data=x, accepted_ndims=(2,), accepted_dtypes=Formats.NUMERIC_DTYPES.value)
    check_valid_array(data=y, accepted_ndims=(1,), accepted_dtypes=Formats.NUMERIC_DTYPES.value, accepted_axis_0_shape=[x.shape[0], ])
    cluster_ids = np.unique(y)
    centroids = np.full(shape=(cluster_ids.shape[0], x.shape[1]), fill_value=-1.0, dtype=np.float32)
    intra_centroid_distances = np.full(shape=(y.shape[0]), fill_value=-1.0, dtype=np.float32)
    obs_cnt = 0

