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

from pathlib import Path

def get_model_init_type(expid):
    '''
    Extract the model and initialization type from an experiment ID string.

    This function splits the experiment ID (`expid`) into its components, extracting the model name 
    and the initialization type, which is assumed to be the last part of the string.

    Parameters:
        expid (str): The experiment ID string, formatted as "model_name_init_type" (e.g., "modelA_01").

    Returns:
        tuple: A tuple containing the model name and initialization type. The model is all components
               before the last underscore, and the initialization type is the part after the last underscore.
    '''
    expid_split = expid.split('_')
    init_type = expid_split[-1]
    model = ''.join(expid_split[:-1])
    return model, init_type

def format_forecast_time(fcrs):
    '''
    Format forecast lead times to Verpy format.

    This function takes a list of forecast lead times in hours and converts them into the Verpy format,
    which multiplies each value by 100. For example, a forecast of 6 hours becomes 600, and 12 hours becomes 1200.

    Parameters:
        fcrs (list of int): A list of forecast lead times in hours (e.g., [6, 12, 18]).

    Returns:
        list of int: A list of forecast lead times in Verpy format, where each value is multiplied by 100.
    '''
    return [fcr * 100 for fcr in fcrs]

def create_tablenames_expids_names(model_names, init_conditions, verif_conditions):
    '''
    Create tablenames, expids, and names to query the SQLite database and save results to CSV files.

    This function generates three lists—`tablenames`, `expids`, and `names`—that are used to query the 
    database and to save the results to CSV files. The tablenames follow the format 
    `{model_name}{initialisation_conditions}_vs_{verification_conditions}`, while the expids 
    follow the format `{model_name}_{initialisation_conditions}`, and the names are in the format 
    `{model_name}_{initialisation_conditions} vs {verification_conditions}`.

    Parameters:
        model_names (list of str): List of model names (e.g., ["modelA", "modelB"]).
        init_conditions (list of str): List of initialisation conditions (e.g., ["MOGLOBAL", "GFS"]).
        verif_conditions (list of str): List of verification conditions (e.g., ["MOGLBOAL", "OBS"]).

    Returns:
        tuple: A tuple containing three lists:
            - `table_names` (list of str): The names of the tables to query.
            - `expids` (list of str): The experiment IDs to associate with the tables.
            - `names` (list of str): The names to be used for CSV files.
    '''
    table_names = []
    expids = []
    names = []
    for model in model_names:
        for init_condition in init_conditions:
            for verif_condition in verif_conditions:
                table_names.append(f"{model}{init_condition}_vs_{verif_condition}")
                expids.append(f"{model}_{init_condition}")
                names.append(f"{model}_{init_condition} vs {verif_condition}")
    return table_names, expids, names


def format_model_name(model_names: list):
    '''
    Corrects the name "fastnet" to "FastNet" in the list of model names.

    This function iterates over a list of model names and replaces any occurrence of "fastnet" 
    with "FastNet".

    Parameters:
        model_names (list of str): A list of model names (e.g., ["fastnet", "other_model"]).

    Returns:
        list of str: The updated list of model names with "fastnet" corrected to "FastNet".
    '''
    for i, name in enumerate(model_names):
        if "fastnet" == name:
            model_names[i] = "FastNet"
    return model_names
