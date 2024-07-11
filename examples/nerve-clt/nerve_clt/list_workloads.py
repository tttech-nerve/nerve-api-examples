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
"""Implementation of the list_workloads command."""

from nerve.workloads import list_workloads, filter_workloads, get_workload_info
from nerve.utils import save_json
from nerve.utils import append_ending, ActionUnsuccessful, DataNotAsExpected


def handle_workloads_list(args):
    """Handles the listing, filtering, and detailing of workloads.

    First, it retrieves a list of workloads and applies filtering based on the criteria specified in the arguments
    (e.g., name, ID, type, version_name, and disabled status). It then fetches detailed information for each workload,
    if verbose output is requested. Supports handling of different workload types including docker, codesys, and vm.
    Unsupported workload types are flagged.

    If human-readable output is requested, it calls `print_human` to print the details.
    Otherwise, it can save the filtered and detailed workloads list to a JSON file if an output filename is provided.

    Parameters:
    - args: A namespace object from argparse containing the command-line arguments.

    Returns:
    - A list of Workload_Information objects, each potentially enriched with detailed information based on
    the command-line arguments.
    """
    #

    # at first we get a list of the workloads, then we filter it, then we add details.
    try:
        workload_list = list_workloads(args.verbose)
    except ActionUnsuccessful as e:
        print(e)
        return

# filtering. Version details can only be filtered in the next go
    result = filter_workloads(workload_list,
                              name=args.name,
                              _id=args.id,
                              _type=args.type,
                              show_disabled=args.disabled)

# adding details to remaining workloads. Note that the details overwrite the entries.
    if (args.verbose):
        print(f"Of those, {len(result)} workloads matched the filter criteria.")
        print("Now fetching details.")

    found_unsupported = False
    for i in range(len(result)):
        try:
            # TODO add more when supporting the other types
            if   (result[i]["type"] == "docker"
                  or result[i]["type"] == "codesys"
                  or result[i]["type"] == "vm"
                  ):
                if (args.verbose):
                    print(f"Fetching details for {result[i]['name']}.")
                result[i] = get_workload_info(_id=result[i]["_id"])
            else:
                found_unsupported = True
        except ActionUnsuccessful as e:
            print(e)
    if found_unsupported:
        print("Some workloads are of unsupported type. Their details are not complete.")

# result is now a list of Workload_Information objects, not yet filtered by version properties
    try:
        result = filter_workloads(result, version_name=args.version_name)
    except DataNotAsExpected as e:
        print("Error filtering the workloads: " + str(e))
        return

# result is now a list of Workload_Information objects.

    if args.human:
        __print_human(result)

    output_filename = None if args.output.lower(
    ) == 'none' else append_ending(args.output, ".json")

    if output_filename:
        save_json(result, output_filename)
        print(f"Saved result to {output_filename}. Contains {len(result)} workload{'s'[:len(result)!=1]}.")

    return result

def __print_human(workload_list):
    if len(workload_list) == 0:
        print("No workloads found.")
        return
    for workload in workload_list:
        if not workload:
            continue
        print(f"Workload: {workload['name']} ({workload['type']})")
        if (workload.get("versions") and len(workload['versions'])):
            for version in workload['versions']:
                if (workload['type'] == "docker"):
                    print(f"   Version: {version['name']}    "+
                          f" Container name: {version['workloadProperties']['container_name']}")
                else:
                    print(f"   Version:{version['name']}")
