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

import sys
import os
import warnings
import random


sys.path = ["../"] + sys.path
from mlint.derived_variables import (
    calc_geostrophic_wind,
    calc_relative_vorticity,
    calc_wind_speed,
    calc_divergence,
    calc_relative_humidity,
    calc_wet_bulb_potential_temperature,
    calc_thickness,
)


import numpy as np
import numpy.ma as ma
import iris
from iris.coords import DimCoord
from iris.cube import Cube


FIXTURE_DATA = "fixture_data.py"
# to remove a warning from iris
iris.FUTURE.save_split_attrs = True

"""
This script generates data that is stored as fixtures in the output file: fixture_data.py
"""


seed_data = np.asarray(
    [
        (
            13.012449799196787,
            16.016828819353144,
            85.58064516129032,
            26.599290780141843,
            14.620881670533644,
            7.297290930506478,
            22.978243978243977,
            16.929721362229103,
        ),
        (
            133.87927107061503,
            133.13720316622693,
            222.97309417040358,
            10.113749190589251,
            14.572604194319087,
            23.508944870390653,
            7497.428571428572,
            11.398487355235169,
        ),
        (
            19.98438239469948,
            48.66097838452787,
            14.793333333333333,
            23.078239608801955,
            40.04036697247707,
            12.486349625715544,
            8.359946390963048,
            9.415140415140415,
        ),
        (
            20.858936240502146,
            16.07314578005115,
            30.083386378103118,
            10.938779414578152,
            85.81402936378467,
            12.57285368802902,
            12.81214514934584,
            10.742527049330644,
        ),
    ]
)

pressure_data = np.asarray(
    [
        [
            (
                13.012449799196787,
                16.016828819353144,
                85.58064516129032,
                26.599290780141843,
                14.620881670533644,
                7.297290930506478,
                22.978243978243977,
                16.929721362229103,
            ),
            (
                133.87927107061503,
                133.13720316622693,
                222.97309417040358,
                10.113749190589251,
                14.572604194319087,
                23.508944870390653,
                7497.428571428572,
                11.398487355235169,
            ),
            (
                19.98438239469948,
                48.66097838452787,
                14.793333333333333,
                23.078239608801955,
                40.04036697247707,
                12.486349625715544,
                8.359946390963048,
                9.415140415140415,
            ),
            (
                20.858936240502146,
                16.07314578005115,
                30.083386378103118,
                10.938779414578152,
                85.81402936378467,
                12.57285368802902,
                12.81214514934584,
                10.742527049330644,
            ),
        ],
        [
            (
                13.012449799196787,
                16.016828819353144,
                85.58064516129032,
                26.599290780141843,
                14.620881670533644,
                7.297290930506478,
                22.978243978243977,
                16.929721362229103,
            ),
            (
                133.87927107061503,
                133.13720316622693,
                222.97309417040358,
                10.113749190589251,
                14.572604194319087,
                23.508944870390653,
                7497.428571428572,
                11.398487355235169,
            ),
            (
                19.98438239469948,
                48.66097838452787,
                14.793333333333333,
                23.078239608801955,
                40.04036697247707,
                12.486349625715544,
                8.359946390963048,
                9.415140415140415,
            ),
            (
                20.858936240502146,
                16.07314578005115,
                30.083386378103118,
                10.938779414578152,
                85.81402936378467,
                12.57285368802902,
                12.81214514934584,
                10.742527049330644,
            ),
        ],
    ]
)


def seed_data_as_cube():
    latitude = DimCoord(
        np.linspace(-90, 90, 4), standard_name="latitude", units="degrees"
    )
    longitude = DimCoord(
        np.linspace(45, 360, 8), standard_name="longitude", units="degrees"
    )
    return Cube(seed_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])


def save_data(f, x, name):
    np.set_printoptions(precision=20)
    np.set_printoptions(suppress=True)
    tab = "    "
    f.write("@pytest.fixture\n")
    f.write(f"def {name}():\n")
    if isinstance(x, ma.MaskedArray):
        x = ma.getdata(x)
    array = repr(x)
    array = array.replace("array", "")
    f.write(tab + "return np.asarray" + array)
    f.write("\n\n")


def no_print(*args, **kwargs):
    pass


warnings.simplefilter("ignore")


def main(print_progress: bool = True):
    my_print = print
    if not print_progress:
        my_print = no_print
    cube = seed_data_as_cube()
    x_wind, y_wind = calc_geostrophic_wind(cube)
    my_print("x_wind")
    my_print(x_wind.data)
    my_print()
    my_print("y_wind")
    my_print(y_wind.data)
    my_print()
    x_wind.units = "m / s"
    y_wind.units = "m / s"
    relative_vorticity = calc_relative_vorticity(x_wind, y_wind)
    my_print("relative vorticity")
    my_print(relative_vorticity.data)
    my_print()
    wind_speed = calc_wind_speed(x_wind, y_wind)
    my_print("wind speed")
    my_print(wind_speed.data)
    my_print()
    divergence = calc_divergence(x_wind, y_wind)
    my_print("divergence")
    my_print(divergence.data)
    my_print()
    x_wind.units = "K"
    y_wind.units = "%"
    relative_humidity = calc_relative_humidity(100, x_wind, y_wind)
    my_print("relative_humidity")
    my_print(relative_humidity.data)
    my_print()
    x_wind.units = "K"
    y_wind.units = "kg kg-1"
    wet_bulb_potential_temperature = calc_wet_bulb_potential_temperature(
        100, x_wind, y_wind
    )
    my_print("wet_bulb_potential_temperature")
    my_print(wet_bulb_potential_temperature.data)
    my_print()
    latitude = DimCoord(
        np.linspace(-90, 90, 4), standard_name="latitude", units="degrees"
    )
    longitude = DimCoord(
        np.linspace(45, 360, 8), standard_name="longitude", units="degrees"
    )
    pressure = DimCoord([500, 1000], standard_name="air_pressure", units="hPa")
    cube = Cube(
        pressure_data,
        dim_coords_and_dims=[(pressure, 0), (latitude, 1), (longitude, 2)],
    )
    thickness = calc_thickness(cube, [500, 1000], pressure_level_str="air_pressure")
    my_print("thickness")
    my_print(thickness.data)
    my_print()

    with open(FIXTURE_DATA, "w") as f:
        f.write("import pytest\n\n\n")
        f.write("import numpy as np\n\n\n")
        f.write("nan = np.nan\n\n\n")
        save_data(f, seed_data, "seed")
        save_data(f, pressure_data, "air_pressure")
        save_data(f, x_wind.data, "x_wind")
        save_data(f, y_wind.data, "y_wind")
        save_data(f, relative_vorticity.data, "relative_vorticity")
        save_data(f, wind_speed.data, "wind_speed")
        save_data(f, divergence.data, "divergence")
        save_data(f, relative_humidity.data, "relative_humidity")
        save_data(
            f, wet_bulb_potential_temperature.data, "wet_bulb_potential_temperature"
        )
        save_data(f, thickness.data, "thickness")


def clean_up():
    os.unlink(FIXTURE_DATA)


if __name__ == "__main__":
    main(False)
