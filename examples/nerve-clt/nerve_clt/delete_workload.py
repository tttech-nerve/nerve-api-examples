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
"""Implementation of the delete_workload command."""

from nerve.workloads import delete_workload_from_ms
from nerve.utils import load_json, append_ending, ActionUnsuccessful
from json import JSONDecodeError


def handle_delete_workload(args):
    """Implementation of the delete_workload command."""
    #
    try:
        filename = append_ending(args.input_file, ".json")
        wl_list = load_json(filename)
    except JSONDecodeError as e:
        print("Could not read input file. ")
        print(e)
        return
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return
    except OSError:
        print(f"Could not open file {filename}.")
        return

    if len(wl_list) > 1 and not args.yes:
        confirmation = input(
            f"This will delete {len(wl_list)} items. Are you sure? (y/n): ")
        if confirmation.lower() != 'y':
            return

    result = []
    for wl in wl_list:
        if (args.verbose):
            print(f"Deleting workload {wl['name']} with id {wl['_id']}.")
        try:
            result.append(delete_workload_from_ms(
                wl["_id"], verbose=args.verbose))
        except ActionUnsuccessful as e:
            print(e)
    print("Deleted: ", result)
