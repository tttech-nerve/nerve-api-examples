from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import yaml
from nerveapi import nodes, session
from nerveapi.utils import append_ending

from .utils import eprint


def handle_deploy_dna(args) -> int:
    # Read DNA file from input file to dict
    filename = append_ending(args.file_name, ".yaml")
    try:
        dna_file_path = Path(filename)
        dna_file_dict = yaml.load(dna_file_path.read_text(), Loader=yaml.FullLoader)
    except yaml.YAMLError as e:
        eprint(f"Could not read input file: {e}")
        return 1
    except FileNotFoundError:
        eprint(f"File {filename} not found.")
        return 1
    except OSError:
        eprint(f"Could not open file {filename}.")
        return 1

    # Get Node from node_name parameter
    node_name = args.node_name
    node = get_node_by_name_and_online(node_name)

    # Fail if no node is found
    if not node:
        return 1

    # Create file from dict to send with request
    dna_file_yaml = yaml.dump(data=dna_file_dict, default_flow_style=False)
    files = {'file': ('file-from-pipeline.yaml', dna_file_yaml)}

    # restart_all_workloads flag
    restart_workloads = args.restart_all_workloads.__str__().lower()

    # Deploy DNA file
    response = session.make_request(f'/nerve/dna/{node["serial_number"]}/target?continueInCaseOfRestart=true&restartAllWorkloads={restart_workloads}', method='PUT', data=dna_file_yaml, files=files)

    if response.status_code == 202:
        print('Successfully pushed DNA File.')
        return 0
    else:
        eprint(f'Error while pushing {response.status_code}: {response.text}')
        print('See https://docs.nerve.cloud/developer_guide/ms-api/ for info on error codes.')
        return 1


def handle_get_dna(args) -> int:
    filename = args.output
    strip_hash = args.strip_hash

    # Get Node from node_name parameter
    node_name = args.node_name
    node = get_node_by_name_and_online(node_name)

    # Fail if no node is found
    if not node:
        return 1

    # Get DNA file
    response = session.make_request(f'/nerve/dna/{node["serial_number"]}/current')
    if response.ok:
        print("DNA file loaded.")
        with ZipFile(BytesIO(response.content)) as myzip:
            with myzip.open(myzip.namelist()[0]) as file:
                try:
                    dna_dict = yaml.safe_load(file)
                    if strip_hash:
                        strip_hash_from_dict(dna_dict)
                    with open(filename, 'w') as outfile:
                        yaml.dump(dna_dict, outfile, default_flow_style=False)
                        print(f"Successfully written DNA file to {filename}.")
                        return 0
                except yaml.YAMLError as e:
                    eprint(f"Could not write output file: {e}")
                    return 1
                except OSError:
                    eprint(f"Could not open output file {filename}.")
                    return 1
    else:
        eprint(f'Retrieving deployed DNA File failed: {response.text}')
        return 1


def get_node_by_name_and_online(filter_string):
    node_list = nodes.create_node_list()
    filtered_node_list = nodes.filter_node_list(name_filter=filter_string, node_list=node_list)
    online_nodes = [node for node in filtered_node_list if node['connection_status'] == 'online']

    if len(online_nodes) == 0:
        eprint(f'No matching online node found.')
        return None
    elif len(online_nodes) > 1:
        online_nodes_names = [device['name'] for device in online_nodes]
        eprint(f'More than one matching online node found, please retry with more restrictive filter: {online_nodes_names}')
        return None
    else:
        node = online_nodes[0]
        print(f'Node {node["name"]} selected.')
        return node


def strip_hash_from_dict(dna_dict):
    for workload in dna_dict['workloads']:
        workload.pop('hash', None)
