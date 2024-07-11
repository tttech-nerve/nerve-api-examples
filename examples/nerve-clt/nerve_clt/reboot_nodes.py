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
"""Implementation of the reboot_nodes command."""

from nerve.utils import (
    load_json,
    append_ending, ActionUnsuccessful)
from nerve.nodes import (
    reboot_node,
    create_node_list_from_node_list,
    all_nodes_have_serial_numbers
)
from json import JSONDecodeError


def handle_reboot_nodes(args):
    """Reboots a list of nodes based on the input JSON file provided through command-line arguments.

    This function reads a JSON file specified by the user, which contains a list of nodes identified
    by their serial numbers, their names or their ids. It attempts to reboot each node individually.
    If a node lacks a serial number, the function tries to rebuild the node list to include serial numbers
    by using available identifying features.

    If multiple nodes are to be rebooted, the function asks the user for confirmation before proceeding.
    The user must explicitly agree by entering 'y' to proceed with the mass reboot operation.

    Parameters:
    - args: A namespace object from argparse containing command-line arguments. Expected to have
            'input_file' attribute specifying the input JSON filename and 'verbose' attribute
            to control verbose output.

    Returns:
    - None: The function prints the outcome of the reboot operation(s) to the console and does not
            return a value. It shows the count of successfully rebooted nodes and, if applicable,
            the number of nodes that failed to reboot.
    """
    #
    filename = append_ending(args.input_file, ".json")
    try:
        node_list = load_json(filename)
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

    if not all_nodes_have_serial_numbers(node_list):
        if args.verbose:
            print(
                "Not all nodes have serial numbers. Fetching serial numbers. Trying to recreate tree.")
        node_list = create_node_list_from_node_list(node_list)

    if len(node_list) > 1 and not args.yes:
        confirmation = input(
            f"This will reboot {len(node_list)} nodes. Are you sure? (y/n): ")
        if confirmation.lower() != 'y':
            return

    count = 0
    for node in node_list:
        if (args.verbose):
            print(f"Rebooting node {node['name']} with id {node['_id']}.")
        try:
            reboot_node(node["serial_number"])
            count += 1
        except ActionUnsuccessful as e:
            print(str(e))

    if count < len(node_list):
        print(f"Rebooted {count} node{'s'[:count!=1]}, failed to reboot {len(node_list) - count} "+
              f"node{'s'[:(len(node_list) - count)!=1]}.")
    else:
        print("Rebooted all nodes.")
