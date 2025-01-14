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

import iris
from iris.cube import CubeList

def _set_input_filename(cycle_time, grid_config_key, grid_name):
    '''
    Create a standardized filename for loading grid data.

    This function generates a filename in the format:
    "{cycle_time}-PT0H-{grid_name}-{grid_config_key}.nc",
    where each parameter contributes to the naming structure.

    Parameters:
        cycle_time (str): A string representation of the cycle time (e.g., '20231118T0600Z').
        grid_config_key (str): A key identifying the grid configuration (e.g., 'high_res', 'low_res').
        grid_name (str): The name of the grid (e.g., 'temperature_grid').

    Returns:
        str: The generated filename with a ".nc" extension.
    '''
    return f"{cycle_time}-PT0H-{grid_name}-{grid_config_key}.nc"


def _set_output_filename(grid_name, cycle_time):
    '''
    Create a standardized filename for saving grid data based on the grid name and cycle time.

    This function generates a filename in the format:
    "{grid_name}_{YYYYMMDD}_{HH}_000.nc",
    where `YYYYMMDD` is the date, `HH` is the hour, and the filename ends with "_000.nc".

    Parameters:
        grid_name (str): The name of the grid (e.g., 'temperature_grid').
        cycle_time (datetime): The cycle time representing the date and hour (e.g., datetime(2023, 11, 18, 6, 0)).

    Returns:
        str: The generated filename with a ".nc" extension.
    '''
    date = cycle_time.strftime("%Y%m%d")
    hour = cycle_time.strftime("%H")
    return f"{grid_name}_{date}_{hour}_000.nc"


def _output_file_exists(output_dir, save_filename):
    '''
    Check if a specified output file exists in the given directory.

    This function verifies whether a file with the given name exists in the specified directory.

    Parameters:
        output_dir (Path): The directory where the file is expected to be located.
        save_filename (str): The name of the file to check.

    Returns:
        bool: `True` if the file exists, `False` otherwise.
    '''
    return (output_dir / save_filename).exists()


def combine_files(cycle_time, grid_name, grid_config_keys, input_dir, output_dir):
    '''
    Combine grid data files for a given cycle time and save the combined output.

    This function loads data from multiple grid configuration files specified by `grid_config_keys`,
    combines the data into a single object, and saves the combined data to the output directory.
    If the output file already exists, the function prints a message and does not overwrite it.

    Parameters:
        cycle_time (datetime): The cycle time representing the date and time (e.g., datetime(2023, 11, 18, 6, 0)).
        grid_name (str): The name of the grid (e.g., 'temperature_grid').
        grid_config_keys (list of str): A list of grid configuration keys (e.g., ['high_res', 'low_res']).
        input_dir (Path): The directory containing the input grid files.
        output_dir (Path): The directory where the combined file will be saved.

    Returns:
        None: The function performs the file combination and saving but does not return a value.
    '''

    input_dir = input_dir / cycle_time.strftime("%Y%m%dT%H%MZ")

    output_dir = output_dir / cycle_time.strftime("%Y")
    # Check if output directory exists and create it if not
    output_dir.mkdir(parents=True, exist_ok=True)

    # check if output file exists
    if _output_file_exists(
        output_dir, _set_output_filename(grid_name, cycle_time)
    ):
        print(f"File {_set_output_filename(grid_name, cycle_time)} already exists")
        return None

    cubelist = CubeList()
    for grid_config_key in grid_config_keys:
        cycle_time_str = cycle_time.strftime("%Y%m%dT%H%MZ")
        filename = _set_input_filename(cycle_time_str, grid_config_key, grid_name)
        cubelist.append(iris.load_cube(input_dir / filename))

    save_filename = _set_output_filename(grid_name, cycle_time)
    iris.save(cubelist, output_dir / save_filename)

