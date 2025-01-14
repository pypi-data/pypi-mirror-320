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


import datetime
from calendar import monthrange
from multiprocessing import Pool
import cdsapi

SURFACE_VAR_FNAME_LIST = [
    "mean_sea_level_pressure",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "2m_temperature",
]

PRESSURE_LEVELS_VAR_NAME = [
    "geopotential",
    "specific_humidity",
    "temperature",
    "u_component_of_wind",
    "v_component_of_wind",
]

PRESSURE_LEVEL_STR_LIST = [
    "50",
    "100",
    "150",
    "200",
    "250",
    "300",
    "400",
    "500",
    "600",
    "700",
    "850",
    "925",
    "1000",
]

FNAME_SUFFIX_DICT = {
    "netcdf": "nc",
    "grib": "grib",
}

def days_in_month(year, month):
    """
    Return the number of days in a given month.

    Parameters:
        year (int): The year (e.g., 2024).
        month (int): The month (1 for January, 12 for December).

    Returns:
        int: The number of days in the given month.
    """
    return monthrange(year, month)[-1]


def get_pressure_retrieval_config(
    var_list, pressure_levels, year, month, days, times, base_output_dir, format
):
    '''
    Create a list of dictionaries for retrieving pressure-level data.

    Parameters:
        var_list (list): List of variables to retrieve (e.g., ['temperature', 'humidity']).
        pressure_levels (list): Pressure levels to include (e.g., [850, 500]).
        year (str): Year for data retrieval (e.g., '2023').
        month (str): Month for data retrieval (e.g., '11' for November).
        days (list): Days of the month for data retrieval (e.g., ['01', '02']).
        times (list): Times of the day for data retrieval (e.g., ['00:00', '12:00']).
        base_output_dir (Path): Base directory for output files.
        format (str): Output file format (e.g., 'netcdf').

    Returns:
        list: A list of dictionaries, each describing a retrieval configuration.
    '''
    dicts = []
    fname_suffix = FNAME_SUFFIX_DICT[format]
    for variable in var_list:
        dicts.append(
            {
                "type": "reanalysis-era5-pressure-levels",
                "variable": variable,
                "pressure_levels": pressure_levels,
                "year": year,
                "month": month,
                "days": days,
                "times": times,
                "output": str(
                    base_output_dir / year / month / f"{variable}.{fname_suffix}"
                ),
                "format": format,
            }
        )
    return dicts


def get_surface_retrieval_config(
    var_list,
    year,
    month,
    days,
    times,
    base_output_dir,
    format,
):
    '''
    Create a list of dictionaries for retrieving surface-level data.

    Parameters:
        var_list (list): List of variables to retrieve (e.g., ['temperature', 'precipitation']).
        year (str): Year for data retrieval (e.g., '2023').
        month (str): Month for data retrieval (e.g., '11' for November).
        days (list): Days of the month for data retrieval (e.g., ['01', '02']).
        times (list): Times of the day for data retrieval (e.g., ['00:00', '12:00']).
        base_output_dir (Path): Base directory for output files.
        format (str): Output file format (e.g., 'netcdf').

    Returns:
        list: A list of dictionaries, each describing a retrieval configuration.
    '''
    dicts = []
    fname_suffix = FNAME_SUFFIX_DICT[format]
    for variable in var_list:
        dicts.append(
            {
                "type": "reanalysis-era5-single-levels",
                "variable": variable,
                "year": year,
                "month": month,
                "days": days,
                "times": times,
                "output": str(
                    base_output_dir / year / month / f"{variable}.{fname_suffix}"
                ),
                "format": format,
            }
        )
    return dicts


def retrieve_variable(dict):
    '''
    Retrieve a variable from the Climate Data Store (CDS) API.

    This function uses the CDS API to retrieve reanalysis data based on the configuration
    specified in the input dictionary. The retrieval can include either pressure-level
    or single-level data, based on the presence of the "pressure_levels" key.

    Parameters:
        dict (dict): A dictionary containing retrieval parameters. Must include:
            - "type" (str): Type of data to retrieve (e.g., 'reanalysis-era5-pressure-levels').
            - "variable" (str): The variable to retrieve (e.g., 'temperature').
            - "year" (str): The year of the data (e.g., '2023').
            - "month" (list): List of months to retrieve (e.g., ['01', '02']).
            - "days" (list): List of days to retrieve (e.g., ['01', '02']).
            - "times" (list): List of times to retrieve (e.g., ['00:00', '12:00']).
            - "format" (str): Output file format (e.g., 'netcdf').
            - "output" (str): Output file path.
            - "pressure_levels" (list, optional): Pressure levels for retrieval, if applicable (e.g., [850, 500]).

    Returns:
        None: The function performs a download and does not return a value.
    '''
    c = cdsapi.Client(timeout=600, quiet=False, debug=True)
    if "pressure_levels" in dict.keys():
        c.retrieve(
            dict["type"],
            {
                "product_type": "reanalysis",
                "variable": dict["variable"],
                "pressure_level": dict["pressure_levels"],
                "year": dict["year"],
                "month": dict["month"],
                "day": dict["days"],
                "time": dict["times"],
                "format": dict["format"],
            },
            dict["output"],
        )

    else:
        c.retrieve(
            dict["type"],
            {
                "product_type": "reanalysis",
                "variable": dict["variable"],
                "year": dict["year"],
                "month": dict["month"],
                "day": dict["days"],
                "time": dict["times"],
                "format": dict["format"],
            },
            dict["output"],
        )
    return None


def times_of_day(step_size):
    '''
    Create a list of times of the day at specified intervals.

    This function generates a list of time strings (in "HH:MM" format) for a 24-hour period,
    starting from midnight (00:00), with intervals determined by the step size.

    Parameters:
        step_size (int): Interval in hours between consecutive times (e.g., 3 for every 3 hours).

    Returns:
        list: A list of time strings in "HH:MM" format.
    '''
    date = datetime.datetime(2023, 5, 1, 0, 0)
    times = []
    for hour in range(0, 25, step_size):
        new_date = date + datetime.timedelta(hours=hour)
        if new_date.strftime("%H:%M") not in times:
            times.append(new_date.strftime("%H:%M"))
    return times


def retrieve_monthly(cycle_time, output_dir, step_size, threads=12, format="netcdf"):
    '''
    Perform data retrieval for the remainder of a month starting from a specified date.

    This function retrieves both pressure-level and surface-level reanalysis data for the
    remainder of the month, using specified parameters such as time steps, output directory,
    and threading for parallel processing.

    Parameters:
        cycle_time (datetime): The starting date and time for data retrieval (e.g., datetime(2023, 11, 15, 0, 0)).
        output_dir (Path): The base output directory for the retrieved data.
        step_size (int): Interval in hours between consecutive times of the day for retrieval (e.g., 6 for every 6 hours).
        threads (int, optional): Number of threads for parallel processing. Default is 12.
        format (str, optional): Output file format for the retrieved data (e.g., "netcdf" or "grib"). Default is "netcdf".

    Returns:
        None: The function performs data retrieval and writes files to the specified directory.
    '''
    print(f"DO THE DATA RETRIEVE for rest of month {cycle_time.month}")
    # DO THE DATA RETRIEVE for rest of new_start_time.month
    num_days_in_month = days_in_month(cycle_time.year, cycle_time.month)
    print(num_days_in_month)
    days = [f"{day:02d}" for day in range(cycle_time.day, num_days_in_month + 1, 1)]
    print(days)
    year = cycle_time.strftime("%Y")
    month = cycle_time.strftime("%m")
    times = times_of_day(step_size)
    pressure_dicts = get_pressure_retrieval_config(
        PRESSURE_LEVELS_VAR_NAME,
        PRESSURE_LEVEL_STR_LIST,
        year,
        month,
        days,
        times,
        output_dir,
        format,
    )
    surface_dicts = get_surface_retrieval_config(
        SURFACE_VAR_FNAME_LIST,
        year,
        month,
        days,
        times,
        output_dir,
        format,
    )
    all_dicts = pressure_dicts + surface_dicts
    print(all_dicts)
    # print(all_dicts.keys())
    # Create output directory if doesn't already exist
    if not (output_dir / year / month).is_dir():
        print(f"creating directory {(output_dir / year / month)}")
        (output_dir / year / month).mkdir(parents=True)

    with Pool(threads) as p:
        p.map(retrieve_variable, all_dicts)


def set_output_filename(grid_name, cycle_time, format):
    '''
    Create a standardized filename for saving grid data based on the grid name, cycle time, and format.

    This function generates a filename in the format:
    "{grid_name}_{YYYYMMDD}_{HH}_000.{format_suffix}",
    where `YYYYMMDD` is the date, `HH` is the hour, and `format_suffix` is determined by the file format.

    Parameters:
        grid_name (str): The name of the grid (e.g., 'temperature_grid').
        cycle_time (datetime): The cycle time representing the date and hour (e.g., datetime(2023, 11, 18, 6, 0)).
        format (str): The file format (e.g., "netcdf", "grib").

    Returns:
        str: The generated filename.
    '''
    date = cycle_time.strftime("%Y%m%d")
    hour = cycle_time.strftime("%H")
    fname_suffix = FNAME_SUFFIX_DICT[format]
    return f"{grid_name}_{date}_{hour}_000.{fname_suffix}"


def output_file_exists(output_dir, save_filename):
    '''
    Check if a specified output file exists in the given directory.

    This function verifies the presence of a file in a specified directory by constructing
    the file path from the directory and filename.

    Parameters:
        output_dir (Path): The directory where the file is expected to be located.
        save_filename (str): The name of the file to check.

    Returns:
        bool: `True` if the file exists, `False` otherwise.
    '''
    return (output_dir / save_filename).exists()