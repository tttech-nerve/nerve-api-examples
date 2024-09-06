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
"""Implementation of the list_nodes command."""

from nerveapi.nodes import create_node_list, filter_node_list
from nerveapi.nodes import get_deployed_workloads_from_node, filter_node_list_for_wl
from nerveapi.utils import ActionUnsuccessful, load_json, save_json, append_ending
from nerveapi.labels import get_labels
from commands.utils import eprint
from json import JSONDecodeError


def handle_list_nodes(args) -> int:
    """Implementation of the list_nodes command.
    
    Returns:
    - int: The exit code to return to the shell. 0 indicates success, while any other value indicates an error.
    """
    #
    # for the moment this is quite inefficient.
    # First, it gets a list of all nodes.
    # In order to do that we need the labels first

    try:
        ms_labels = get_labels()
    except ActionUnsuccessful as e:
        eprint(e)
        return 1

    if (args.verbose):
        print("Starting node list.")
    try:
        node_list = create_node_list(args.verbose, ms_labels)
    except ActionUnsuccessful as e:
        eprint(e)
        return 1

    if (args.verbose):
        print("Node list created. Has", len(node_list), " nodes.")

# Now filter for node filters
    filtered_list = filter_node_list(
        name_filter=args.node_name,
        path_filter=args.node_path,
        node_version_filter=args.node_version,
        label_filter=args.node_labels,
        model_filter=args.node_model,
        node_list=node_list)

    if len(filtered_list) > 9:
        print(
            f"Warning: {len(filtered_list)} nodes found."+
            " This may take a while. Consider using more specific node filters.")

    if (args.verbose):
        print("Filtered for node criteria. List now has",
              len(node_list), " nodes.")
        print("Getting workload data.")


# Now add workload info for the online ones.
    online_nodes = []
    offline_nodes = []

    for index in range(len(filtered_list)):
        if (filtered_list[index]["connection_status"] == "online"):
            if args.verbose:
                print("Getting workloads for node",
                      filtered_list[index]["name"])
            dwl = get_deployed_workloads_from_node(
                filtered_list[index]["serial_number"])
            node = filtered_list[index]
            node["workloads"] = dwl
            online_nodes.append(node)
        else:
            offline_nodes.append(filtered_list[index])

# Now filter for workload properties, if any workloads filters are specified.
    if (args.workload_name or
            args.workload_id or
            args.workload_version_name or
            args.workload_version_id or
            args.workload_status or
            args.workload_type
        ):
        filtered_for_wl = filter_node_list_for_wl(
            name_filter=args.workload_name,
            _id_filter=args.workload_id,
            version_name_filter=args.workload_version_name,
            version_id_filter=args.workload_version_id,
            status_filter=args.workload_status,
            type_filter=args.workload_type,
            node_list=online_nodes)
    else:
        filtered_for_wl = online_nodes

    if args.verbose:
        print("Complete.")
        print("The system has a total of", len(node_list), " nodes.")
        print("Of those,", len(filtered_list),
              "nodes match the filter criteria regarding nodes.")
        print("Of those,", len(online_nodes), "nodes are online,",
              len(offline_nodes), "nodes are offline.")
        print("Of the online nodes,", len(filtered_for_wl),
              "nodes match the filter criteria regarding workloads.")

    if args.human:
        print("")
        print("")
        print("Found following nodes and workloads:")
        print("")
        for node in filtered_for_wl:
            print(f"Node path: {'/'.join(node['path'])}   Name:{node['name']}   Model:{node['model']}"+
                  f"   Version:{node['version']}")
            for wl in node['workloads']:
                print(
                    f"   Workload: {wl['name']}/{wl['version_name']} ({wl['state']})")
            print("")

    filename = append_ending(args.file_name, ".json")

    result_list = []
    if args.add:
        if args.verbose:
            print(f"Adding was specified. Therefore reading existing data from input file {filename}.")
        try:
            result_list = load_json(filename)
        except JSONDecodeError:
            eprint(
                f"File {filename} is not a valid JSON file. Ignoring the file as input, creating a new list.")
        except OSError:
            eprint(
                f"Error reading file {filename}. Ignoring the file as input, creating a new list.")

    if result_list is None:
        eprint(
            "Input file {filename} is not found, empty or not a valid JSON file. Creating a new list.")
        result_list = []

    if len(filtered_for_wl) == 0:
        print("No nodes/workloads found matching the criteria.")

    result_list.extend(filtered_for_wl)
    if args.verbose:
        print(f"Writing to file {filename}.")
    save_json(result_list, filename)
    print(f"Created result file {filename} with {len(result_list)} node{'s'[:len(result_list)!=1]}.")
    return 0
# Path: src/commands/control_workloads.py
