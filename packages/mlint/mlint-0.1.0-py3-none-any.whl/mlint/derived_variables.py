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

import os
import pathlib
import re
import numpy as np
import iris
import ncdata
import ncdata.iris_xarray

import metpy


def convert_cube_to_pint(cube, check_crs=True):
    '''
    Convert an Iris Cube to a Pint Quantity with MetPy integration.

    This function extracts the variable from an Iris Cube, converts the data to a 
    xarray Dataset, parses the variable using MetPy's CF conventions, and then 
    returns the data as a Pint Quantity object. Optionally checks if the CRS 
    (coordinate reference system) is present in the data.

    Parameters:
        cube (iris.cube.Cube): The Iris Cube to be converted.
        check_crs (bool, optional): If True, the function checks whether the 'metpy_crs' 
                                    attribute is present in the xarray data. Defaults to True.

    Returns:
        pint.Quantity: The data as a Pint Quantity.

    Raises:
        UserWarning: If neither `var_name` nor `name` is defined for the cube, or if
                     the 'metpy_crs' attribute is not found when `check_crs` is True.
    '''
    if cube.var_name is not None:
        var_name = cube.var_name
    elif cube.name() is not None:
        var_name = cube.name()
    else:
        raise UserWarning('define var_name or name of cube')

    dataset = ncdata.iris_xarray.cubes_to_xarray(cube)
    data_array = dataset.metpy.parse_cf(var_name)

    if check_crs:
        try:
            getattr(data_array, 'metpy_crs')
        except AttributeError:
            raise UserWarning('metpy_crs not generated')
   
    pint = data_array.metpy.quantify()
    
    return pint 


def convert_pint_to_cube(pint, var_name=None):
    '''
    Convert a Pint Quantity to an Iris Cube.

    This function takes a Pint Quantity and converts it back into an Iris Cube. 
    It first dequantifies the Pint object to remove the units and converts the 
    underlying data into an xarray Dataset. Then, it attempts to create an Iris 
    Cube from the data. If the resulting CubeList contains more than one cube, 
    a warning is raised.

    Parameters:
        pint (pint.Quantity): The Pint Quantity to convert.
        var_name (str, optional): The name to assign to the variable in the 
                                   resulting Iris Cube. Defaults to None.

    Returns:
        iris.cube.Cube: The resulting Iris Cube.

    Raises:
        UserWarning: If the CubeList contains more than one cube.
    '''
    data_array = pint.metpy.dequantify().drop_vars('metpy_crs')
    cubelist = ncdata.iris_xarray.cubes_from_xarray(data_array.to_dataset(name=var_name))

    if isinstance(cubelist, iris.cube.CubeList) and len(cubelist) == 1:
        cube = cubelist[0]
    else:
        raise UserWarning('was expecting the cubelist to only contain one cube')

    return cube


def calc_geostrophic_wind(geopotential_height_cube):
    '''
    Calculate the geostrophic wind from a geopotential height cube.

    This function takes an Iris Cube of geopotential height, converts it to a 
    Pint Quantity, and then uses MetPy to calculate the geostrophic wind in both 
    the x and y directions. The function returns two Iris Cubes corresponding 
    to the geostrophic wind components in the x and y directions.

    Parameters:
        geopotential_height_cube (iris.cube.Cube): The Iris Cube containing the 
                                                   geopotential height data.

    Returns:
        tuple: A tuple containing two Iris Cubes:
            - The first Cube is the x-component of the geostrophic wind.
            - The second Cube is the y-component of the geostrophic wind.
    '''
    geopotential_height = convert_cube_to_pint(geopotential_height_cube, check_crs=True)

    x_wind, y_wind =  metpy.calc.geostrophic_wind(geopotential_height)

    x_wind_cube = convert_pint_to_cube(x_wind, var_name='x_wind_geostrophic')
    y_wind_cube = convert_pint_to_cube(y_wind, var_name='y_wind_geostrophic')

    return x_wind_cube, y_wind_cube


def calc_relative_vorticity(x_wind_cube, y_wind_cube):
    '''
    Calculate the relative vorticity from wind components.

    This function takes Iris Cubes of the x and y components of the wind, converts them 
    to Pint Quantities, and computes the relative vorticity using MetPy. The resulting 
    vorticity is then converted back to an Iris Cube.

    Parameters:
        x_wind_cube (iris.cube.Cube): The Iris Cube containing the x-component of the wind.
        y_wind_cube (iris.cube.Cube): The Iris Cube containing the y-component of the wind.

    Returns:
        iris.cube.Cube: An Iris Cube containing the calculated relative vorticity.
    '''
    x_wind = convert_cube_to_pint(x_wind_cube, check_crs=True)
    y_wind = convert_cube_to_pint(y_wind_cube, check_crs=True)

    vort = metpy.calc.vorticity(x_wind, y_wind)

    cube = convert_pint_to_cube(vort, var_name='relative_vorticity')

    return cube


def calc_wind_speed(x_wind_cube, y_wind_cube):
    '''
    Calculate wind speed from the x and y components of the wind.

    This function takes Iris Cubes of the x and y components of the wind, converts them 
    to Pint Quantities, and computes the wind speed using MetPy. The resulting wind speed 
    is then converted back to an Iris Cube.

    Parameters:
        x_wind_cube (iris.cube.Cube): The Iris Cube containing the x-component of the wind.
        y_wind_cube (iris.cube.Cube): The Iris Cube containing the y-component of the wind.

    Returns:
        iris.cube.Cube: An Iris Cube containing the calculated wind speed.
    '''
    x_wind = convert_cube_to_pint(x_wind_cube)
    y_wind = convert_cube_to_pint(y_wind_cube)

    ws = metpy.calc.wind_speed(x_wind, y_wind)

    cube = convert_pint_to_cube(ws, var_name='wind_speed')

    return cube


def calc_relative_humidity(pressure_in_hPa=None, 
        temperature_cube=None, specific_humidity_cube=None):
    '''
    Calculate relative humidity from pressure, temperature, and specific humidity.

    This function computes the relative humidity at a given pressure level using the 
    temperature and specific humidity provided as Iris Cubes. If the pressure is supplied 
    as a 1D numpy array, it is broadcast to match the shape of the temperature cube.

    Parameters:
        pressure_in_hPa (float or numpy.ndarray): Pressure at the level(s) in hPa. 
            Can be a scalar or a 1D numpy array.
        temperature_cube (iris.cube.Cube): Iris Cube containing the temperature at the pressure level.
        specific_humidity_cube (iris.cube.Cube): Iris Cube containing the specific humidity at the pressure level.

    Returns:
        iris.cube.Cube: An Iris Cube containing the calculated relative humidity. 
        The variable name is set to `relative_humidity` or `relative_humidity_<pressure>_hPa` 
        if pressure is provided as a scalar.
    '''

    if isinstance(pressure_in_hPa, np.ndarray):
        pressure = iris.util.broadcast_to_shape(pressure_in_hPa, 
            temperature_cube.shape, (0,))
    else:
        pressure = pressure_in_hPa

    pressure = pressure * metpy.units.units.hPa

    temperature = convert_cube_to_pint(temperature_cube)
    specific_humidity = convert_cube_to_pint(specific_humidity_cube)
    
    rh = metpy.calc.relative_humidity_from_specific_humidity(
        pressure, temperature, specific_humidity
        )

    rh_cube = convert_pint_to_cube(rh)

    if isinstance(pressure_in_hPa, np.ndarray):
        rh_cube.var_name = 'relative_humidity'
    else:
        rh_cube.var_name = f'relative_humidity_{int(np.rint(pressure_in_hPa))}_hPa'

    return rh_cube


def calc_divergence(x_wind_cube, y_wind_cube):
    '''
    Calculate divergence from the x and y components of the wind.

    This function computes the divergence field using the x and y wind components 
    provided as Iris Cubes. The input cubes are converted to Pint Quantities 
    for calculation using MetPy, and the resulting divergence is returned as an Iris Cube.

    Parameters:
        x_wind_cube (iris.cube.Cube): Iris Cube containing the x-component of the wind.
        y_wind_cube (iris.cube.Cube): Iris Cube containing the y-component of the wind.

    Returns:
        iris.cube.Cube: An Iris Cube containing the calculated divergence field.
        The variable name of the output cube is set to `divergence`.
    '''
    x_wind = convert_cube_to_pint(x_wind_cube, check_crs=True)
    y_wind = convert_cube_to_pint(y_wind_cube, check_crs=True)

    vort = metpy.calc.divergence(x_wind, y_wind)

    cube = convert_pint_to_cube(vort, var_name='divergence')

    return cube


def calc_wet_bulb_potential_temperature(pressure_in_hPa=None, 
        temperature_cube=None, specific_humidity_cube=None):
    '''
    Calculate the wet-bulb potential temperature.

    This function computes the wet-bulb potential temperature for a given pressure level,
    temperature, and specific humidity. The inputs are Iris Cubes for temperature and
    specific humidity, along with the pressure value(s) in hPa. The calculation uses 
    MetPy's thermodynamic functions and converts the result back to an Iris Cube.

    Parameters:
        pressure_in_hPa (float or numpy.ndarray): Pressure at the level(s) of interest, in hPa. 
            Can be a scalar or a 1D numpy array matching the vertical dimension of the cubes.
        temperature_cube (iris.cube.Cube): Iris Cube containing the temperature data (in Kelvin).
        specific_humidity_cube (iris.cube.Cube): Iris Cube containing the specific humidity data 
            (dimensionless, typically kg/kg).

    Returns:
        iris.cube.Cube: An Iris Cube containing the calculated wet-bulb potential temperature (in Kelvin).
        The variable name of the output cube is set to `WBPT` or `WBPT_<pressure>_hPa`.
    '''

    if isinstance(pressure_in_hPa, np.ndarray):
        pressure = iris.util.broadcast_to_shape(pressure_in_hPa, 
            temperature_cube.shape, (0,))
    else:
        pressure = pressure_in_hPa

    pressure = pressure * metpy.units.units.hPa

    temperature = convert_cube_to_pint(temperature_cube)
    specific_humidity = convert_cube_to_pint(specific_humidity_cube)

    dewpoint = metpy.calc.dewpoint_from_specific_humidity(pressure, specific_humidity)

    wbpt = metpy.calc.wet_bulb_potential_temperature(pressure, temperature, dewpoint)

    wbpt_cube = convert_pint_to_cube(wbpt)

    if isinstance(pressure_in_hPa, np.ndarray):
        wbpt_cube.var_name = 'WBPT'
    else:
        wbpt_cube.var_name = f'WBPT_{int(np.rint(pressure_in_hPa))}_hPa'

    return wbpt_cube 


def calc_thickness(geopotential_height_cube, pressure_levels=None, pressure_level_str='pressure'):
    '''
    Calculate the geopotential thickness between two pressure levels.

    The thickness is the difference in geopotential height between two specified 
    pressure levels, typically used to analyze atmospheric layers (e.g., 1000–500 hPa layer).

    Parameters:
        geopotential_height_cube (iris.cube.Cube): Cube containing geopotential height data (in meters).
        pressure_levels (list or tuple of int): A pair of pressure levels (in hPa) for thickness calculation. 
            The upper level (lower pressure) should be first in the list.
        pressure_level_str (str): The name of the coordinate representing pressure levels in the cube.

    Returns:
        iris.cube.Cube: A new Cube containing the calculated thickness between the specified pressure levels.
        The variable name of the output cube is set to `thickness_<upper>_<lower>_hPa`.

    Raises:
        UserWarning: If the pressure levels are not provided in the correct order (upper level first).
    '''
   
    if pressure_levels[1] < pressure_levels[0]:
        raise UserWarning('unexpected ordering of pressures')

    cube_1 = geopotential_height_cube.extract(iris.Constraint(**{ pressure_level_str:pressure_levels[0]}))
    cube_2 = geopotential_height_cube.extract(iris.Constraint(**{ pressure_level_str:pressure_levels[1]}))

    cube = cube_1 - cube_2

    var_name = 'thickness_1000_500_hPa'
    cube.rename(var_name)
    cube.var_name = var_name


    return cube

"""
#function to calculate specific humidity from relative humidity and temperature
def calc_specific_humidity(cube_temp, cube_rh):
    '''
    Calculate the specific humidity from temperature and relative humidity.

    This function calculates the specific humidity using temperature and relative humidity. 
    The process involves first calculating the dewpoint from the temperature and relative humidity,
    and then using the dewpoint and temperature to calculate the specific humidity.

    Parameters:
        cube_temp (iris.cube.Cube): A Cube containing temperature data in degrees Celsius.
        cube_rh (iris.cube.Cube): A Cube containing relative humidity data in percentage.

    Returns:
        numpy.ndarray: An array of specific humidity values.
    '''
    #calculate the dewpoint from the relative humidity and temperature    
    dewpoint = metpy.calc.dewpoint_from_relative_humidity(cube_temp.data  * units.degC , cube_rh.data * units.percent)

    #calculate the specific humidity from the dewpoint and temperature
    specific_humidity = metpy.calc.specific_humidity_from_dewpoint(cube_temp.data * units.degC , dewpoint.data * units.degC)

    return specific_humidity
"""

"""
def calc_derived_variables(filename_in, list_variables, write_netcdf=True, output_folder=None):
    '''
    Calculate derived meteorological variables from a NetCDF input file.

    Parameters:
        filename_in (str): Path to the input NetCDF file containing the data.
        list_variables (list of str): List of variables to calculate. Options include:
            - 'x_wind_geostrophic', 'y_wind_geostrophic'
            - 'wet_bulb_potential_temperature', 'wet_bulb_potential_temperature_<pressure>_hPa'
            - 'relative_vorticity', 'relative_vorticity_<pressure>_hPa'
            - 'relative_humidity', 'relative_humidity_<pressure>_hPa'
            - 'divergence', 'divergence_<pressure>_hPa'
            - 'wind_speed', 'wind_speed_<pressure>_hPa', 'wind_speed_10m'
            - 'thickness_<lower_pressure>_<upper_pressure>_hPa'
        write_netcdf (bool): Whether to save the derived variables as a NetCDF file. Defaults to True.
        output_folder (str, optional): Directory to save the output NetCDF file, required if `write_netcdf` is True.

    Returns:
        iris.cube.CubeList: A list of derived variables as Iris cubes.

    Raises:
        UserWarning: If a requested variable is not recognized or implemented, 
                     or if `output_folder` is missing while `write_netcdf=True`.
    '''

    list_all_vars = [
            'x_wind_geostrophic',
            'y_wind_geostrophic',
            'wet_bulb_potential_temperature_\d+_hPa',
            'wet_bulb_potential_temperature',
            'relative_vorticity_\d+_hPa',
            'relative_vorticity',
            'relative_humidity_\d+_hPa',
            'relative_humidity',
            'divergence_\d+_hPa',
            'divergence',
            'wind_speed_\d+_hPa',
            'wind_speed',
            'wind_speed_10m',
            'thickness_\d+_\d+_hPa'
        ]

    for var in list_variables:
        if not any(re.fullmatch(re_str, var) for re_str in list_all_vars):
            raise UserWarning(f'unrecognised variable requested: {var}')

    if write_netcdf:
        if output_folder is None:
            raise UserWarning(f'if outputting netCDF, need to specify output_folder')

    cubelist_in = iris.load(filename_in)
    print(cubelist_in)
    cubelist_out = iris.cube.CubeList([])

    list_variables_to_iterate = list_variables.copy()

    if ('x_wind_geostrophic' in list_variables) or ('y_wind_geostrophic' in list_variables):
        list_variables_to_iterate.append('wind_geostrophic')
        try: 
            list_variables_to_iterate.remove('x_wind_geostrophic')
        except ValueError:
            pass
        try: 
            list_variables_to_iterate.remove('y_wind_geostrophic')
        except ValueError:
            pass
   
    for var in list_variables_to_iterate:
        print(var)
        var_split = var.split('_')

        if var_split[0] == 'thickness':
            geopotential_height_cube = cubelist_in.extract_cube(iris.NameConstraint(var_name='geopotential_height'))

            var_cube = calc_thickness(geopotential_height_cube, 
                pressure_levels=[float(var_split[2]), float(var_split[1])])

            var_cube.var_name = var 

            cubelist_out.append(var_cube)

        elif var_split[0:2] == ['relative', 'vorticity']:
            if len(var_split) > 2:
                pressure_in_hPa = float(var_split[2])      
                pressure_constraint = iris.Constraint(pressure=pressure_in_hPa)   
            else:     
                pressure_constraint = None

            x_wind_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='x_wind_0') & pressure_constraint)
            y_wind_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='y_wind_0') & pressure_constraint)

            var_cube = calc_relative_vorticity(x_wind_cube, y_wind_cube)

            var_cube.var_name = var 

            cubelist_out.append(var_cube)

        elif var_split[0:2] == ['wind', 'speed']:
            if len(var_split) == 4: # calculate ws on specified pressure level
                pressure_in_hPa = float(var_split[2])      
                pressure_constraint = iris.Constraint(pressure=pressure_in_hPa) 
                ext = '_0'  
            elif len(var_split) == 3: # calculate 10m ws
                pressure_constraint = None
                ext = ''
            else: # calculate ws on all pressure levels
                pressure_constraint = None
                ext = '_0'

            x_wind_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='x_wind' + ext) & pressure_constraint)
            y_wind_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='y_wind' + ext) & pressure_constraint)

            var_cube = calc_wind_speed(x_wind_cube, y_wind_cube)

            var_cube.var_name = var 

            cubelist_out.append(var_cube)

        elif var_split[0] == 'divergence':
            if len(var_split) > 1:
                pressure_in_hPa = float(var_split[1])      
                pressure_constraint = iris.Constraint(pressure=pressure_in_hPa)    
            else:     
                pressure_constraint = None  

            x_wind_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='x_wind_0') & pressure_constraint)
            y_wind_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='y_wind_0') & pressure_constraint)

            var_cube = calc_divergence(x_wind_cube, y_wind_cube)

            var_cube.var_name = var 

            cubelist_out.append(var_cube)

        elif var_split[0:4] == ['wet', 'bulb' ,'potential', 'temperature']: 
            if len(var_split) > 4:
                pressure_in_hPa = float(var_split[4])
                pressure_constraint = iris.Constraint(pressure=pressure_in_hPa)    
            else:     
                pressure_constraint = None  

            temperature_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='air_temperature_0') & pressure_constraint)

            specific_humidity_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='specific_humidity') & pressure_constraint)

            if pressure_constraint is None:
                pressure_in_hPa = temperature_cube.coord('pressure').points

            var_cube = calc_wet_bulb_potential_temperature(pressure_in_hPa=pressure_in_hPa, 
                temperature_cube=temperature_cube, 
                specific_humidity_cube=specific_humidity_cube)

            var_cube.var_name = var 

            cubelist_out.append(var_cube)

        elif var_split[0:2] == ['relative', 'humidity']: 
            if len(var_split) > 2:
                pressure_in_hPa = float(var_split[2])
                pressure_constraint = iris.Constraint(pressure=pressure_in_hPa)    
            else:     
                pressure_constraint = None  

            temperature_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='air_temperature_0') & pressure_constraint)

            specific_humidity_cube = cubelist_in.extract_cube(
                iris.NameConstraint(var_name='specific_humidity') & pressure_constraint)

            if pressure_constraint is None:
                pressure_in_hPa = temperature_cube.coord('pressure').points

            var_cube = calc_relative_humidity(pressure_in_hPa=pressure_in_hPa, 
                temperature_cube=temperature_cube, 
                specific_humidity_cube=specific_humidity_cube)

            var_cube.var_name = var 

            cubelist_out.append(var_cube)

        elif var == 'wind_geostrophic':
            geopotential_height_cube = cubelist_in.extract_cube(iris.NameConstraint(var_name='geopotential_height'))

            x_wind_cube, y_wind_cube = calc_geostrophic(geopotential_height_cube)

            if 'x_wind_geostrophic' in list_variables:
                cubelist_out.append(x_wind_cube)

            if 'y_wind_geostrophic' in list_variables:
                cubelist_out.append(y_wind_cube)

        else:
             raise UserWarning(f'variable not implemented yet: {var}')

    if write_netcdf:
        path = pathlib.Path(filename_in)
        filename_out = os.path.join(output_folder, path.stem + '-derived' + path.suffix)
        print(filename_out)
        iris.save(cubelist_out, filename_out)
        
    return cubelist_out
"""
