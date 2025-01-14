# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# (C) British Crown Copyright 2017-2020 Met Office.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

import warnings
import numpy as np
import pytest

from .fixtures import *
from .fixture_data import *
from mlint.derived_variables import (
    convert_cube_to_pint,
    convert_pint_to_cube,
    calc_geostrophic_wind,
    calc_relative_vorticity,
    calc_wind_speed,
    calc_relative_humidity,
    calc_divergence,
    calc_wet_bulb_potential_temperature,
    calc_thickness,
)


def test_convert_cube_to_pint(seed_as_cube, seed):
    pint = convert_cube_to_pint(seed_as_cube)
    result = pint.to_numpy()
    assert np.array_equal(seed, result)


def test_convert_cube_to_pint_no_crs_check(seed_as_cube, seed):
    pint = convert_cube_to_pint(seed_as_cube, check_crs=False)
    result = pint.to_numpy()
    assert np.array_equal(seed, result)


def test_convert_pint_to_cube(seed_as_cube, seed):
    pint = convert_cube_to_pint(seed_as_cube)
    # remove warnings from iris, this is just a test
    warnings.filterwarnings("ignore", module="iris")
    cube = convert_pint_to_cube(pint)
    assert np.array_equal(seed, cube.data)


def test_calc_geostrophic_wind(seed_as_cube, x_wind, y_wind):
    xwind, ywind = calc_geostrophic_wind(seed_as_cube)
    assert np.array_equal(xwind.data, x_wind)
    assert np.array_equal(ywind.data, y_wind)


def test_calc_relative_vorticity(seed_as_cube, relative_vorticity):
    xwind, ywind = calc_geostrophic_wind(seed_as_cube)
    # iris will complain otherwise
    xwind.units = "m / s"
    ywind.units = "m / s"
    rv = calc_relative_vorticity(xwind, ywind)
    assert np.array_equal(rv.data, relative_vorticity)


def test_calc_wind_speed(seed_as_cube, wind_speed):
    xwind, ywind = calc_geostrophic_wind(seed_as_cube)
    # iris will complain otherwise
    xwind.units = "m / s"
    ywind.units = "m / s"
    ws = calc_wind_speed(xwind, ywind)
    assert np.all(np.isclose(ws.data, wind_speed))


def test_calc_relative_humidity(seed_as_cube, relative_humidity):
    xwind, ywind = calc_geostrophic_wind(seed_as_cube)
    # iris will complain otherwise
    xwind.units = "K"
    ywind.units = "%"
    rh = calc_relative_humidity(100, xwind, ywind)
    assert np.array_equal(rh.data, relative_humidity)


def test_calc_divergence(seed_as_cube, divergence):
    xwind, ywind = calc_geostrophic_wind(seed_as_cube)
    # iris will complain otherwise
    xwind.units = "m / s"
    ywind.units = "m / s"
    d = calc_divergence(xwind, ywind)
    assert np.array_equal(d.data, divergence)


def test_calc_wet_bulb_potential_temperature(
    seed_as_cube, wet_bulb_potential_temperature
):
    # remove warnings from dask, this is just a test
    warnings.filterwarnings("ignore", module="dask")
    xwind, ywind = calc_geostrophic_wind(seed_as_cube)
    # iris will complain otherwise
    xwind.units = "K"
    ywind.units = "kg kg-1"
    wbpt = calc_wet_bulb_potential_temperature(100, xwind, ywind)
    assert np.isnan(wbpt.data).all()


def test_calc_thickness(air_pressure, thickness):
    latitude = DimCoord(
        np.linspace(-90, 90, 4), standard_name="latitude", units="degrees"
    )
    longitude = DimCoord(
        np.linspace(45, 360, 8), standard_name="longitude", units="degrees"
    )
    pressure = DimCoord([500, 1000], standard_name="air_pressure", units="hPa")
    cube = Cube(
        air_pressure, dim_coords_and_dims=[(pressure, 0), (latitude, 1), (longitude, 2)]
    )
    thickness = calc_thickness(cube, [500, 1000], pressure_level_str="air_pressure")
