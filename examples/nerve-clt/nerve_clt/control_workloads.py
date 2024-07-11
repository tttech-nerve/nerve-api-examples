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
"""Implementation of the control_workloads command."""

from nerve.utils import (
    load_json,
    append_ending, ActionUnsuccessful)
from nerve.nodes import (
    control_workload,
    create_node_list_from_node_list,
    all_nodes_have_serial_numbers,
    all_workloads_have_device_ids
)
from json import JSONDecodeError


def handle_start_workloads(args):
    """Implementation of the control_workloads command."""
    return handle_control_workloads("start", args)


def handle_stop_workloads(args):
    """Implementation of the control_workloads command."""
    if args.force:
        return handle_control_workloads("force_stop", args)
    else:
        return handle_control_workloads("stop", args)


def handle_restart_workloads(args):
    """Implementation of the control_workloads command."""
    return handle_control_workloads("restart", args)


def handle_control_workloads(action, args):
    """Implementation of the control_workloads command."""
    #
    input_filename = append_ending(args.input_file, ".json")
    try:
        node_list = load_json(input_filename)
    except JSONDecodeError as e:
        print("Could not read input file. ")
        print(e)
        return
    except FileNotFoundError:
        print(f"File {input_filename} not found.")
        return

    if ((not all_nodes_have_serial_numbers(node_list)) or
            (not all_workloads_have_device_ids(node_list))):
        if args.verbose:
            print("In the input file, some workloads miss their ids,"+
                  " or nodes their serial numbers. Trying to find those details.")
        node_list = create_node_list_from_node_list(node_list, True, args.verbose)
    # Now all data (serial_number and device_id ) needed to control should be available.

    if len(node_list) > 1:
        confirmation = input(
            f"This will {action} {len(node_list)} workloads. Are you sure? (y/n): ")
        if confirmation.lower() != 'y':
            return

    count = 0
    failed = 0
    for node in node_list:
        for wl in node.get("workloads"):

            if (args.verbose):
                print(
                    f"Will {action} workload {wl['device_id']} on {node['serial_number']}.")

            try:
                control_workload(action, node["serial_number"], wl["device_id"])
                count += 1
            except ActionUnsuccessful as e:
                failed += 1
                print(e)

    if failed:
        print(f"Succeeded to initialize '{action}' command on", count,
              f"workload{'s'[:count!=1]}, failed on", failed, ".")
    elif count == 0:
        print("No workloads to control.")
    else:
        print(f"Succeded to initialize '{action}'  command on all workloads.")
    return count
