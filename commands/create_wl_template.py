# Copyright(c) 2024 TTTech Industrial Automation AG.
#
# ALL RIGHTS RESERVED.
# Usage of this software, including source code, netlists, documentation,
# is subject to restrictions and conditions of the applicable license
# agreement with TTTech Industrial Automation AG or its affiliates.
#
# All trademarks used are the property of their respective owners.
#
# TTTech Industrial Automation AG and its affiliates do not assume any liability
# arising out of the application or use of any product described or shown
# herein. TTTech Industrial Automation AG and its affiliates reserve the right to
# make changes, at any time, in order to improve reliability, function or
# design.
#
# Contact Information:
# support@tttech-industrial.com
# TTTech Industrial Automation AG, Schoenbrunnerstrasse 7, 1040 Vienna, Austria
"""Implementation of the create_wl_template command."""

from nerveapi.workloads import get_workload_info
from nerveapi.utils import load_json, append_ending, ActionUnsuccessful, DataNotAsExpected, complainIfKeysAreNotInDict
from nerveapi.datastructures import create_workload_definition_from_json
from dataclasses import asdict
import json
from json import JSONDecodeError


def handle_create_wl_template(args):
    """Handles the creation of a workload template based on an input JSON file.

    This function loads a workload list from a specified JSON file, then fetches detailed information
    for the first workload in the list from the management system. It supports workloads of type 'docker' 
    and rewrites the definition to create a template from which a new workload can be created. The resulting
    template is saved to a specified output file.
    Note that only the first workload in the list is considered for creating the template but that all versions of this 
    workload are considered. If you want to create only one version, remove the others from the input file.


    Parameters:
    - args: A namespace object from argparse containing command-line arguments. Expected to have 
            'input_file' and 'output_file' attributes specifying the input and output JSON filenames, 
            and a 'verbose' attribute to control verbose output.

    Returns:
    - None: The function writes the resulting template to a file and does not return a value.
    """
    #    
    input_filename = append_ending(args.input_file, ".json")
    output_filename = append_ending(args.output_file, ".json")
    try:
        wl_list = load_json(input_filename)
    except JSONDecodeError as e:
        print("Could not read input file. ")
        print(e)
        return
    except FileNotFoundError:
        print(f"File {input_filename} not found.")
        return
    except OSError:
        print(f"Could not open file {input_filename}.")
        return

    if len(wl_list) > 1:
        print("Multiple workloads in the input list."+
              "The template will be created only from the first one.")

    wl = wl_list[0]
    try:
        complainIfKeysAreNotInDict(wl, ["_id", "versions"])
    except DataNotAsExpected:
        print("The workload in the input list does have the expected format. _id or versions is missing.")
        return

    if args.verbose and len(wl.get('versions')) > 1:
        print(f"The workload in the input list has {len(wl.get('versions'))} versions.")

    # The workload info is needed to get the id of the workload, to see if we 
    # add to the workload or create a new one
    
    if (args.verbose):
        print(f"Getting workload info for {wl.get('name')} with id {wl.get('_id')}.")
    try:
        wl_info = get_workload_info(_id=wl["_id"], versions=wl.get("versions"))
    except ActionUnsuccessful as e:
        print(e)
        return

    if wl_info["type"] != "docker":
        print(f"Workload type {wl_info['type']} is not yet supported.")
        return

    try:
        wl_def_as_dict = rewrite_original_source_definition(wl_info)
        wl_def = create_workload_definition_from_json(wl_def_as_dict)
    except DataNotAsExpected as e:
        print(e)
        return


    with open(output_filename, 'w') as output_file:
        json.dump(asdict(wl_def), output_file, indent=4)
        print(f"Template saved to {output_filename}.")
    return asdict(wl_def)

# Takes a json and sees it contains the way the source is defined in the MS.
# Since we use a simplified defintion, this rewrites the definition in order to be interpretable


def rewrite_original_source_definition(wl_info_dict):
    """Rewrites the original source definition in the workload information dictionary.
     
    This is done to rewrite the information of the docker source to a simplified format which is used in the template.

    The function iterates through all versions of the workload information.

    Parameters:
    - wl_info_dict: A dictionary containing the workload information fetched from the management system. 
                    It is expected to include a 'versions' key with a list of version dictionaries.

    Returns:
    - A modified version of the input dictionary where the source definitions have been rewritten to the 
      simplified format. This dictionary is suitable for use in creating workload templates.
    """
    #
    for version in wl_info_dict["versions"]:
        if version["dockerFileOption"] == "path":

            version["source"] = {"path": version["dockerFilePath"]}

            if auth_credentials := version.get("auth_credentials"):
                version["source"]["auth_credentials"] = auth_credentials

        else:
            raise DataNotAsExpected(f"Docker Option {version['dockerFileOption']} is not yet supported.")

    return wl_info_dict
