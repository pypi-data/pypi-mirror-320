import pytest

import numpy as np

import iris
from iris.coords import DimCoord
from iris.cube import Cube
from .fixture_data import seed


# to remove a warning from iris
iris.FUTURE.save_split_attrs = True


@pytest.fixture
def seed_as_cube(seed):
    latitude = DimCoord(
        np.linspace(-90, 90, 4), standard_name="latitude", units="degrees"
    )
    longitude = DimCoord(
        np.linspace(45, 360, 8), standard_name="longitude", units="degrees"
    )
    return Cube(seed, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
