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
"""Implementation of the create_workload command."""

import json
from nerveapi.utils import append_ending, ActionUnsuccessful
from nerveapi.datastructures import create_workload_definition_from_json
from nerveapi.workloads import create_workload_in_ms
from commands.utils import eprint


def handle_create_workload(args) -> int:
    """Implementation of the create_workload command.
    
    Returns:
    - int: The exit code to return to the shell. 0 indicates success, while any other value indicates an error.
    """
    #
    template = {}
    filename = append_ending(args.template, ".json")
    try:
        with open(filename, 'r') as file:
            template = json.load(file)
    except FileNotFoundError:
        eprint(
            f"File {filename} not found."
        )
        return 1
    except json.JSONDecodeError:
        eprint(f"File {filename} does not contain valid JSON.")
        return 1

    try:
        workload_definition = create_workload_definition_from_json(template)
    except Exception as e:
        eprint(f"Error creating workload definition from template file: {e}")
        return 1
    
    if args.verbose:
        print(f"Creating workload {workload_definition.name}.")

    # just adds the worklad to the ms
    try:
        create_workload_in_ms(workload_definition,
                              sequential=args.sequential, verbose=args.verbose)
    except ActionUnsuccessful as e:
        eprint(e)
        return 1
    
    print("Workload created.")
    return 0
    
