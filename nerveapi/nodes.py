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
"""Handling of Nerve nodes."""

from .utils import (
    ActionUnsuccessful,
    DataNotAsExpected,
    serverMessage,
    complainIfKeysAreNotInDict,
    complainIfNotAList,
    create_regex,
    findDictByValue
)


from typing import Optional, List

from .session import make_request
from pprint import pprint
import json


def create_node_list(verbose=False, ms_labels=None):
    """Creates a list of nodes from the Nerve management system.

    Simply wraps the create_node_list_and_tree function and returns the node list.
    See there for details.
    """
    #
    [tree, node_list] = create_node_list_and_tree(verbose, ms_labels)
    return node_list


def filter_node_list(
        name_filter: Optional[str] = None,
        path_filter: Optional[str] = None,
        node_version_filter: Optional[str] = None,
        label_filter: Optional[str] = None,
        model_filter: Optional[str] = None,
        node_list: Optional[List[dict]] = None) -> List[dict]:
    """Filters a list of nodes based on ID, name, path, version, label, and model.

    Applies regex-based filters to a given list of node dictionaries, returning only those nodes
    that match all provided filter criteria.

    Parameters:
    - name_filter (str, optional): Regex pattern to filter nodes by name.
    - path_filter (str, optional): Regex pattern to filter nodes by path.
    - node_version_filter (str, optional): Regex pattern to filter nodes by version.
    - label_filter (str, optional): Regex pattern to filter nodes by label.
    - model_filter (str, optional): Regex pattern to filter nodes by model.
    - node_list (List[dict], optional): The list of node dictionaries to filter.

    Returns:
    - List[dict]: A list of node dictionaries that match all provided filters.
    """
    #

    name_pattern = create_regex(name_filter)
    path_pattern = create_regex(path_filter)
    node_version_pattern = create_regex(node_version_filter)
    label_pattern = create_regex(label_filter)
    model_pattern = create_regex(model_filter)

    filtered_nodes = []

    for node in node_list:
        path_string = "/".join(node['path'])
        labels = node['labels']

        # If there is no label filter, we don't need to check for label matches
        if label_filter:
            labels_matches = False
            for label in labels:
                label_string = ":".join(label)
                if label_pattern.match(label_string):
                    labels_matches = True
                    break
            if not labels_matches:
                continue

        if not name_pattern.match(node['name']):
            continue
        if not path_pattern.match(path_string):
            continue
        if not node_version_pattern.match(node['version']):
            continue
        if not model_pattern.match(node['model']):
            continue
        filtered_nodes.append(node)
    return filtered_nodes


def filter_node_list_for_wl(
        name_filter: Optional[str] = None,
        _id_filter: Optional[str] = None,
        version_name_filter: Optional[str] = None,
        version_id_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        node_list: List[dict] = None) -> List[dict]:
    """Filters a list of nodes to find specific workloads based on various criteria.

    This function iterates through a list of nodes and their installed workloads, and filters
    these nodes based on the provided criteria. Only nodes containing workloads that match all the given
    filters are retained in the final list.

    Parameters:
    - name_filter (str, optional): Regex pattern to filter workloads by their name.
    - _id_filter (str, optional): Regex pattern to filter workloads by their ID.
    - version_name_filter (str, optional): Regex pattern to filter workloads by their version name.
    - version_id_filter (str, optional): Regex pattern to filter workloads by their version ID.
    - status_filter (str, optional): Regex pattern to filter workloads by their status.
    - type_filter (str, optional): Regex pattern to filter workloads by their type.
    - node_list (List[dict], optional): The list of node dictionaries, each potentially containing multiple workloads.

    Returns:
    - List[dict]: A list of nodes, where each node contains only the workloads
                  that match the specified filters. The data of each node in the list
                  is preserved, but the 'workloads' key of each node will only include the
                  filtered workloads.
    """    
    #
    name_pattern = create_regex(name_filter)
    _id_pattern = create_regex(_id_filter)
    version_name_pattern = create_regex(version_name_filter)
    version_id_pattern = create_regex(version_id_filter)
    status_pattern = create_regex(status_filter)
    type_pattern = create_regex(type_filter)

    filtered_nodes = []
    for node in node_list:
        wl_list = []

        for wl in node['workloads']:
            if not name_pattern.match(wl['name']):
                continue
            if not _id_pattern.match(wl['_id']):
                continue
            if not version_name_pattern.match(wl['version_name']):
                continue
            if not version_id_pattern.match(wl['version_id']):
                continue
            if not status_pattern.match(wl['state']):
                continue
            if not type_pattern.match(wl['type']):
                continue
            wl_list.append(wl)
        if len(wl_list) > 0:
            node['workloads'] = wl_list
            filtered_nodes.append(node)
    return filtered_nodes


def get_deployed_workloads_from_node(serialNumber):
    """Retrieves a list of deployed workloads for a specific node identified by its serial number.

    Makes a request to the management system to fetch detailed information about all workloads
    deployed on the specified node.

    Parameters:
    - serialNumber (str): The serial number of the node.

    Returns:
    - list: A list of dictionaries, each representing a deployed workload on the node.

    Raises:
    - ActionUnsuccessful: If the request to the management system fails or if the retrieved data
                          is not in the expected format.
    """
    #

    response = make_request(f"/nerve/workload/node/{serialNumber}/devices")
    if not response:
        error_msg = serverMessage(response)
        raise ActionUnsuccessful(error_msg)

    data = response.json()
    wl_list = []
    for wl in data:
        complainIfKeysAreNotInDict(
            wl, ["device_name", "device_model_name", "service_list"])

        name = wl.get("device_name")
        type = wl.get("device_model_name")  # worklaod type
        service_list = wl.get("service_list")

        if len(service_list) != 2:
            raise ActionUnsuccessful(
                "Expected 2 services in response to getting deployed workloads.")

        service = service_list[0]
        property_list = service.get("property_list")
        property = property_list[0]

        complainIfKeysAreNotInDict(property, ["value"])
        value_as_string = property.get("value")
        value = json.loads(value_as_string)

        complainIfKeysAreNotInDict(
            value, ["workloadId", "versionId", "workloadVersionName"])
        workload_id = value.get("workloadId")
        version_id = value.get("versionId")
        workload_version_name = value.get("workloadVersionName")

        service = service_list[1]
        property_list = service.get("property_list")
        property = property_list[2]

        complainIfKeysAreNotInDict(property, ["name", "options", "value"])
        if property.get("name") != "State":
            raise ActionUnsuccessful(
                "Expected name:State in response to getting deployed workloads.")
        options = property.get("options")

        complainIfNotAList(options)
        value = property.get("value")

        state = options[value]

        deployed_wl_info = {
            "name": name,
            "type": type,
            "_id": workload_id,
            "version_id": version_id,
            "version_name": workload_version_name,
            "state": state,
            "device_id": wl.get("id")
        }
        wl_list.append(deployed_wl_info)
    return wl_list


def create_node_list_and_tree(verbose=False, ms_labels=None):
    """Creates both a hierarchical tree structure and a flat list of all nodes retrieved from the management system.

    This function fetches the root node of the node tree from the management system and recursively
    retrieves all child nodes to construct both a hierarchical representation (tree) of nodes and a flat
    list of nodes. The hierarchical tree is useful for understanding the organization and relationships
    between nodes, while the flat list provides a simple enumeration of all nodes.

    Parameters:
    - verbose (bool, optional): If True, prints additional information about the progress of the function.
    - ms_labels (dict, optional): The labels information to be able to insert the data in clear text, not as ID.

    Returns:
    - tuple: A tuple containing two elements:
        - The first element is a dictionary representing the hierarchical tree structure of nodes.
          Each node is a dictionary with keys '_id', 'name', 'type', and 'children', where 'children'
          is a list of child nodes represented in the same manner.
        - The second element is a list of dictionaries, where each dictionary represents a node with
          additional details such as 'serial_number', 'connection_status', 'version', 'model', and 'labels'.

    Raises:
    - ActionUnsuccessful: If any request to the management system fails, or if the retrieved data does
                          not meet expected formats or contain expected keys, indicating an issue with
                          the data retrieval or structure.
    """
    #

    response = make_request("/nerve/tree-node/type/root")
    if not response:
        error_msg = serverMessage(response)
        print(f"Action unsuccessful: {error_msg}")
        raise ActionUnsuccessful(error_msg)

    data = response.json()[0]
    complainIfKeysAreNotInDict(data, ["_id", "name", "type"])

    if verbose:
        pprint("Reading node tree root.")
    [children, node_list] = get_children_of(data['_id'], type=data['type'], path=[
                                            'root'], verbose=verbose, ms_labels=ms_labels)

    tree = {
        '_id': data.get('_id'),
        'name': data.get('name'),
        'type': data.get('type'),
        'children': children
    }

    return [tree, node_list]


def get_children_of(_id, type, path=[], verbose=False, ms_labels=None):
    """This function retrieves the children of a node in the node tree recursively.

    Recursion stops when a node is a leaf node (type 'node').
    The function returns a list of children and a list of nodes, with the 
    node details fileed in.

    Parameters:
    - _id (str): The ID of the node whose children are to be retrieved.
    - type (str): The type of the node. Must be 'folder', 'root', or 'unassigned'.
    - path (list, optional): The path to the current node in the tree
    - verbose (bool, optional): If True, prints additional information about the progress of the function.
    - ms_labels (dict, optional): The labels information to be able to insert the data in clear text, not as ID.
    """
    node_list = []

    if type == 'folder' or type == 'root':
        response = make_request(f"/nerve/tree-node/parent/{_id}")
    elif type == 'unassigned':
        response = make_request("/nerve/tree-node/child-type/unassigned")
    else:
        raise ValueError("Type must be 'folder', 'root', or 'unassigned'")

    if not response:
        error_msg = "Server did not return a valid response"  # Adjusted for example
        raise Exception("ActionUnsuccessful", error_msg)

    data = response.json()  # we expect this to be a list of children

    children = []
    for child in data:
        complainIfKeysAreNotInDict(child, ["_id", "name", "type"])

        # Building the path for the current child
        current_path = path[:]  # Clone the current path
        current_path.append(child["name"])

        child_dict = {
            '_id': child['_id'],
            'name': child['name'],
            'type': child['type'],
            'path': current_path  # Include the path in the structure
        }

        if child['type'] == 'folder' or child['type'] == 'unassigned':
            if verbose:
                print("Getting data of node tree item:", child_dict['name'])
            [child_dict["children"], nodes] = get_children_of(
                child_dict['_id'], type=child_dict['type'], path=current_path, ms_labels=ms_labels)
            node_list.extend(nodes)

        children.append(child_dict)

        if child['type'] == "node":
            device = child['device']
            serialNumber = device['serialNumber']
            label_ids = device['labels']
            device_labels = []
            if ms_labels is not None:
                device_labels = create_device_label_list(label_ids, ms_labels)
            node_list.append(
                {
                    '_id':   child_dict['_id'],
                    'name':  child_dict['name'],
                    'serial_number': serialNumber,
                    'connection_status': device['connectionStatus'],
                    'version': device['currentFWVersion'],
                    'model': device['model'],
                    'labels': device_labels,
                    # remove the name of the node from the path
                    'path':  child_dict['path'][:-1]
                }
            )
    return [children, node_list]


def create_device_label_list(ids: list[str], ms_labels: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    """Creates a nice list of dictionary of labels for a device from the IDs of the labels and the label list."""
    node_labels = []
    for id in ids:
        if id in ids:
            node_labels.append(ms_labels.get(id))
        else:
            raise DataNotAsExpected(
                f"Label with id {id} not found in the label list.")
    return node_labels


def reboot_node(serial_number: str):
    """Reboots a node with the specified serial number.

    parameters:
    - serial_number (str): The serial number of the node to reboot.

    Raises:
    - ActionUnsuccessful: If the request to the management system fails.
    """
    response = make_request(
        f"/nerve/node/{serial_number}/reboot", data={"timeout": 10000}, method='POST')
    if not response:
        error_msg = serverMessage(response)
        raise ActionUnsuccessful(
            f"Error trying to reboot node {serial_number}. Server returned: {error_msg}")
    return


# This function takes a list of nodes, where a node can be identified with serial_number, _id or name and fills all the 
# rest of the information of the node. It returns a list of nodes with all the information filled.
# If the node is not found, it is not included in the result.
# The order of precedence is: serial_number, _id, name


def create_node_list_from_node_list(partial_list: List[dict], with_workloads=False, verbose = False) -> List[dict]:
    """Creates a list of nodes with all information filled from a partial list of nodes.

    It uses the serial number, or name to find the node. This way the provider of the input list
    does not need to know the serial number which is used for identification in the management system,
    but name or _id can be used as well.

    parameters:
    - partial_list (List[dict]): A list of dictionaries representing nodes with partial information.
    - with_workloads (bool, optional): If True, retrieves the workloads of the nodes as well.
    """
    #
    [node_tree, node_list] = create_node_list_and_tree(verbose)

    complainIfNotAList(partial_list)

    result_list = []

    for node in partial_list:
        found_node = None        
        if node.get('serial_number'):
            if verbose:
                print("Searching for node with serial number", node['serial_number'])
            found_node = findDictByValue(
                node_list, 'serial_number', node['serial_number'])
        elif node.get('name'):
            if verbose:
                print("Searching for node with name", node['name'])
            found_node = findDictByValue(node_list, 'name', node['name'])
        else:
            if verbose:
                print("No info to identify node found! I need at either serial_number or name.")
            continue

        if found_node:
            if verbose:
                print("Found node:", found_node['name'])

            if with_workloads and node.get('workloads'):
                found_node['workloads'] = create_wl_list_from_wl_list(
                    node['workloads'], found_node, verbose)
            else:
                if verbose:
                    print("No workloads to add!")
                found_node['workloads'] = []
    
            result_list.append(found_node)
        else:
            if verbose:
                print("Node not found!")    

    return result_list

# ensures that the device_id is present in the workloads of the nodes
# uses name or version_name to find the workload in the complete list

def create_wl_list_from_wl_list(partial_list, node, verbose=False):
    """Creates a list with all information filled from a partial list of workloads.

    It uses the device_id, name, or version_name to find the workload. This way the provider of the input list
    does not need to know the device_id which is used for identification in the management system,

    parameters:
    - partial_list (List[dict]): A list of dictionaries representing workloads with partial information.
    - node: The node information where the workloads are deployed.
    """
    #
    if (node["connection_status"] == "online"):
        if verbose:
            print("Getting workloads for node",
                    node["name"])
        complete_list = get_deployed_workloads_from_node(node["serial_number"])
    else:
        if verbose:
            print("Node is offline. No workloads to get.")
        return []
    
    if not complete_list:
        if verbose:
            print("No workloads found for node.")
        return []

    result = []
    for wl in partial_list:
        found_wl = None
        if wl.get('device_id'):
            if verbose:
                print("Searching for workload with device_id", wl['device_id'])
            found_wl = findDictByValue(
                complete_list, 'device_id', wl['device_id'])
        elif wl.get('name'):
            if verbose:
                print("Searching for workload with name", wl['name'])
            found_wl = findDictByValue(complete_list, 'name', wl['name'])
        elif wl.get('version_name'):
            if verbose:
                print("Searching for workload with version_name", wl['version_name'])
            found_wl = findDictByValue(
                complete_list, 'version_name', wl['version_name'])
        else:
            if verbose:
                print("No info to identify workload found! I need device_id, name or version_name.")
            continue
        if found_wl:
            result.append(found_wl)
            if verbose:
                print("Found workload:", found_wl['name'])

    return result


def all_nodes_have_serial_numbers(node_list: List[dict]):
    """Checks if all nodes within a node list have serial numbers."""
    for node in node_list:
        if not node.get('serial_number'):
            return False
    return True


def all_workloads_have_device_ids(node_list: List[dict]):
    """Checks if all workloads within a node list have device IDs."""
    for node in node_list:
        for wl in node["workloads"]:
            if not wl.get('device_id'):
                return False
    return True


def control_workload(action, serial_number, device_id):
    """Controls a workload on a specific node.

    Parameters:
    - action (str): The action to perform on the workload. Must be 'start', 'stop', 'restart', or 'force_stop'.
    - serial_number (str): The serial number of the node.
    - device_id (str): The device ID of the workload.

    Raises:
    - ValueError: If the action is not one of 'start', 'stop', 'restart', or 'force_stop'.
    - ActionUnsuccessful: If the request to the management system fails.
    """
    #
    if action not in ["start", "stop", "restart", "force_stop"]:
        raise ValueError(
            "Action must be 'start', 'stop', 'force_stop', or 'restart'")

    force_stop = False
    if action == "force_stop":
        action = "STOP"
        force_stop = True

    action = action.upper()

    data = {
        "command": action,
        "deviceId": device_id,
        "forceStop": force_stop,
        "serialNumber": serial_number,
        "timeout": 0
    }

    response = make_request("/nerve/workload/controller", data=data,
                            method='POST', workaround="Inject_Session_Token_To_Controller_Call")
    if not response:
        error_msg = serverMessage(response)
        raise ActionUnsuccessful(f"Error trying to initialize '{action}' on workload {device_id} on node {serial_number} server returned: {error_msg}")
    return
