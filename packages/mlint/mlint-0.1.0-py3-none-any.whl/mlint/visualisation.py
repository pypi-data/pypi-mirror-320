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

import matplotlib as mpl
#there is a display issue when running on servers, this stops it:
mpl.use('Agg')
import matplotlib.pyplot as plt
import iris
import iris.quickplot as qplt
import iris.analysis.cartography
import os
from mlint.calculate_derived_variables import  *

def plot_cube(cube, levels, title, output_dir, figname, latitude_bounds=[-90,90], longitude_bounds=[-180,180],plot_type="basic", convert="none"):
    '''
    Create a contour plot from a given cube of data with customizable plot settings.

    This function generates a contour plot from the provided `cube`, with support for custom latitude and longitude bounds,
    unit conversion, and different plot types. The plot is saved as a PNG image to the specified output directory.

    Parameters:
        cube (iris.cube.Cube): A Cube containing the data to be plotted.
        levels (list or numpy.ndarray): The levels at which to draw the contours.
        title (str): The title to be added to the plot.
        output_dir (str or pathlib.Path): The directory where the plot will be saved.
        figname (str): The filename for the saved plot.
        latitude_bounds (list of float, optional): Latitude bounds for the plot. Defaults to [-90, 90].
        longitude_bounds (list of float, optional): Longitude bounds for the plot. Defaults to [-180, 180].
        plot_type (str, optional): The type of plot to create. Can be "basic" or "opmet". Defaults to "basic".
        convert (str, optional): The unit to which the cube should be converted. Defaults to "none".

    Returns:
        None: This function saves the plot as a PNG image to the specified directory.
    '''

    if cube is not None:

        #this is required to prevent plotting errors along the 
        #Greenwich Meridian
        subset = cube.intersection(longitude=(-180, 180))
        cube=subset

        #cut out the section required by the bounds
        subset = cube.intersection(longitude=longitude_bounds)
        cube=subset
 
        print("lat, lon bounds are",latitude_bounds, longitude_bounds)
        latitude_constraint = iris.Constraint(latitude=lambda cell: latitude_bounds[0] < cell < latitude_bounds[1])
        subset = cube.extract(latitude_constraint)
        cube=subset

        if(convert!="none"):
            cube.convert_units(convert)

        #plot the ml_model global data                       
        plot_select(plot_type, cube, levels)
                     
        # Add coastlines to the map created by contour.
        plt.gca().coastlines()

        #Add title
        plt.title(title)
             
        #Add coordinates and gridlines
        grid = plt.gca().gridlines(draw_labels=True,linestyle='-',linewidth=0.5)
        grid.xlabels_top = True
        grid.ylabels_right = True


        #create the directory if it doesn't exist.
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
                        
        #save the plot
        print("saving file ",output_dir+figname)
        plt.savefig(output_dir+figname, format="png",dpi=240, bbox_inches='tight' )
                     
        #close the plotting
        plt.clf()

def plot_select(plot_type, cube, levels):
    '''
    Create different types of contour plots based on the plot type.

    This function generates contour plots based on the provided plot type. It uses `qplt.contourf` 
    for filled contour plots and `qplt.contour` for line contour plots. Different colormaps and 
    styles are applied depending on the `plot_type`.

    Parameters:
        plot_type (str): The type of plot to generate. Possible values are:
            - "basic": A basic contour plot.
            - "diff": A contour plot showing differences, with a red-blue color map.
            - "pressure": A contour plot with pressure data and labeled contour lines.
            - "air_temp": A contour plot for air temperature with dashed contour lines.
        cube (iris.cube.Cube): A Cube containing the data to plot.
        levels (list or numpy.ndarray): The levels at which to draw the contours.
    '''
    if(plot_type=="basic"):
        qplt.contourf(cube, levels)

    if(plot_type=="diff"):
        qplt.contourf(cube, levels, cmap="brewer_RdBu_11")

    if(plot_type=="pressure"):
        contour=qplt.contour( cube, levels, linewidths=0.5  )
        plt.clabel(contour, inline=False, fontsize=4, colors="black")
               
    if(plot_type=="air_temp"):
        qplt.contourf(cube, levels,   cmap='gist_ncar')
        contour=qplt.contour(cube, levels, colors='grey', linewidths=0.2, linestyles='dashed')
        plt.clabel(contour, inline=False, fontsize=4, colors='black' )

