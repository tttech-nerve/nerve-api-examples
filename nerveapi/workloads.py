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
"""Workload Handling."""

from typing import List, Optional
from dataclasses import asdict
import time

from .session import make_request
from .datastructures import (
    Workload_Definition,
    WorkloadVersion_Docker_Definition,
    RemoteConnection_Definition,
    UploadFile,
    DockerRepoPath,
)
from .utils import create_regex, ActionUnsuccessful, serverMessage, complainIfKeysAreNotInDict, complainIfNotAList


def list_workloads(verbose: bool = False) -> List[dict]:
    """Fetches a list of workloads from the server.

    :param verbose: If True, prints additional information during execution.
    :return: A list of workload dictionaries.
    """
    #
    response = make_request("/nerve/v2/workloads")
    if not response:
        raise ActionUnsuccessful(f"Could not retrieve list of workloads. {serverMessage(response)}")
    wl_response = response.json()
    # Use the number of workloads returned.
    count = wl_response.get("count", 0)
    if verbose:
        print(f"Will try to fetch a total of {count} workloads")

    response = make_request(f"/nerve/v2/workloads?limit={count}")
    if not response:
        raise ActionUnsuccessful(f"Could not retrieve list of workloads. {serverMessage(response)}")

    wl_list_json = response.json().get("data", [])
    if verbose:
        print(f"Got {len(wl_list_json)} workloads")

    return wl_list_json


def filter_workloads(
    workloads: List[dict],
    name: Optional[str] = None,
    _id: Optional[str] = None,
    _type: Optional[str] = None,
    show_disabled: Optional[bool] = None,
    version_name: Optional[str] = None,
    version_id: Optional[str] = None,
) -> List[dict]:
    """Filters workloads based on provided criteria.

    :param workloads: A list of workloads to filter.
    :param name: Name of the workload to match (supports regex).
    :param _id: ID of the workload to match (supports regex).
    :param type: Type of the workload to match.
    :param show_disabled: If False, only enabled workloads are returned.
    :param version_name: Version name of the workload to match (supports regex).
    :param version_id: Version ID of the workload to match (supports regex).
    :return: A list of workloads that match the filters.
    """
    #
    if not workloads:
        # raise DataNotAsExpected("Workloads must not be None.")
        return []
    complainIfNotAList(workloads)

    name_pattern = create_regex(name)
    id_pattern = create_regex(_id)
    version_name_pattern = create_regex(version_name)
    version_id_pattern = create_regex(version_id)
    filtered_workloads = []

    for workload in workloads:
        if (
            name_pattern.match(workload["name"])
            and id_pattern.match(workload["_id"])
            and (not _type or _type == workload["type"])
            and (show_disabled or not workload["disabled"])
        ):
            if version_name:
                filtered_versions = []
                for version in workload.get("versions", []):
                    if version_name_pattern.match(version.get("name", "")) and version_id_pattern.match(
                        version.get("_id", "")
                    ):
                        filtered_versions.append(version)
                if filtered_versions:
                    workload["versions"] = filtered_versions
                    filtered_workloads.append(workload)
            else:
                filtered_workloads.append(workload)

    return filtered_workloads


def get_workload_info(
    _id: Optional[str] = None, name: Optional[str] = None, versions: Optional[list] = None
) -> Optional[dict]:
    """Retrieves workload information by ID or name.

    :param _id: The ID of the workload to retrieve.
    :param name: The name of the workload to retrieve. Can be used instead of ID.
    :versions: A list of versions, where only the _id is taken into consideration to filter the versions.
    :return: The workload information dictionary or None if not found.
    """
    #
    if (_id and name) or (not _id and not name):
        raise ActionUnsuccessful("Specify either an ID or a name, not both or neither.")

    if _id:
        response = make_request(f"/nerve/v2/workloads/{_id}")
        if not response:
            raise ActionUnsuccessful(
                f"Could not retrieve details for workload with ID {_id}. " +
                f"The server responded: {serverMessage(response)}"
            )
        wl = response.json()
    else:
        # get the list filtered by name
        response = make_request(f'/nerve/v2/workloads?filterBy={{"name":"{name}"}}')
        json_response = response.json()
        complainIfKeysAreNotInDict(json_response, ["data"])
        wl_list_json = json_response["data"]

        wl_list_json = [wl for wl in wl_list_json if wl["name"] == name]
        if len(wl_list_json) > 1:
            raise ActionUnsuccessful(
                f"Multiple workloads found with name {name}. Cannot proceed, please use id instead."
            )
        if len(wl_list_json) == 0:
            return None
        wl = wl_list_json[0]

    if versions:
        # Reformat the versions list to a list containing the ids only.
        version_ids = [version["_id"] for version in versions]

        wl["versions"] = [version for version in wl["versions"] if version["_id"] in version_ids]

    return wl


def create_workload_in_ms(
    wl_definition: Workload_Definition, sequential: bool = False, verbose: bool = False
) -> Optional[str]:
    """Creates a workload in the management system. If the workload already exists, adds new versions to it.

    :param wl_definition: The definition of the workload to create.
    :param sequential: If True, adds versions sequentially and waits for each to complete.
    :param verbose: If True, prints additional information during execution.
    :return: The ID of the created or updated workload, or None on failure.
    """
    #
    # First either get the workload info or create the workload.
    wl_info = get_workload_info(name=wl_definition.name)
    if wl_info is None:
        if verbose:
            print(f"Workload does not yet exist in ms. Creating workload {wl_definition.name}.")
        try:
            wl_info = create_workload_without_versions_in_ms(wl_definition, verbose)
        except ActionUnsuccessful as e:
            print(e)
            return None
    else:
        if verbose:
            print(f"Workload {wl_definition.name} already exists in ms. Skipped creation.")
    _id = wl_info["_id"]

    # Now we can add the versions.
    if wl_definition.type == "docker":
        for version_def in wl_definition.versions:
            if verbose:
                print(f"Adding version {version_def.name} to workload {wl_definition.name}.")
            add_workload_version_in_ms(_id, version_def, sequential, verbose)
        return _id
    else:
        raise ActionUnsuccessful("Only Docker type is supported right now.")


def create_workload_without_versions_in_ms(wl_definition: Workload_Definition, verbose: bool = False) -> dict:
    """Creates a workload without adding versions to it.

    :param wl_definition: The workload definition.
    :param verbose: If True, prints additional information during execution.
    :return: The JSON response from the server.
    """
    #
    if wl_definition.type == "docker":
        wl_as_dict = asdict(wl_definition)
        wl_as_dict["versions"] = []

        files = {
            # Empty content for multipart form.
            "file1": ("", "", "application/octet-stream"),
            # Another empty content.
            "file2": ("", "", "application/octet-stream"),
        }

        response = make_request("/nerve/v2/workloads", method="POST", data=wl_as_dict, files=files)
        if not response:
            raise ActionUnsuccessful(f"Creation of workload {wl_definition.name} failed. {serverMessage(response)}")
        if verbose:
            print(f"Workload {wl_definition.name} created successfully.")

        return response.json()


def add_workload_version_in_ms(
    wl_id: str, wl_version_def: WorkloadVersion_Docker_Definition, sequential: bool = False, verbose: bool = False
) -> Optional[str]:
    """Adds a version to an existing workload.

    :param wl_id: The ID of the workload to which the version will be added.
    :param wl_version_def: The version definition.
    :param sequential: If True, waits for the download to complete before returning.
    :param verbose: If True, prints additional information during execution.
    :return: The workload ID on success, or None if sequential mode is not used.
    """
    #
    # This function takes the current workload info, modifies it and sends it back to the server. This results in a new 
    # version being added.
    wl_info = get_workload_info(_id=wl_id)  # First, get the current workload information to modify it.
    if not wl_info:
        raise ActionUnsuccessful(f"Workload {wl_id} not found. Cannot add version.")

    if wl_info["type"] == "docker":
        prepare_docker_version_dict_from_wl_def(wl_version_def, wl_info)
    else:
        raise ActionUnsuccessful("Only Docker type is supported right now.")

    files = {
        # Empty content to satisfy multipart form requirements.
        "file1": ("", "", "application/octet-stream"),
    }
    response = make_request("/nerve/v2/workloads", method="PATCH", data=wl_info, files=files)
    if not response:
        raise ActionUnsuccessful(
            f"Creation of workload version {wl_version_def.name} failed. {serverMessage(response)}"
        )
    if verbose:
        print(f"Successfully added workload version {wl_version_def.name}.")
        print("The system will start downloading the workload version now.")

    if not sequential:
        return
    wait_for_completion_of_workload_version_download(wl_id)


def wait_for_completion_of_workload_version_download(wl_id: str) -> str:
    """Waits for the download of a workload version to complete.

    :param wl_id: The ID of the workload.
    :return: The ID of the workload.
    """
    time_still_left = 300
    print("Downloading", end="", flush=True)
    while True:
        time.sleep(1)
        print(".", end="", flush=True)
        time_still_left -= 1
        wl_info = get_workload_info(_id=wl_id)
        if not wl_info:
            print("")
            raise ActionUnsuccessful(f"Unexpected issue: cannot get info for workload {wl_id} anymore.")
        the_added_wl_version = wl_info["versions"][-1]
        if not the_added_wl_version.get("isDownloading", False):
            print("\nWorkload version download complete.")
            break
        if time_still_left == 0:
            print("\nWorkload version download timeout. Won't wait any longer, but download will continue.")
            break
    return wl_id


def prepare_docker_version_dict_from_wl_def(wl_version_def, wl_info):
    """Prepares a dictionary for a Docker workload version definition.

    :param wl_version_def: The Docker workload version definition.
    :param wl_info: The workload information dictionary.
    """
    #
    wl_info["versions"] = [asdict(wl_version_def)]
    wl_info["versions"][0]["releaseName"] = wl_version_def.name

    # Remove limits from dict if not set. The API cannot handle None values.
    if wl_info["versions"][0]["workloadProperties"]["limit_memory"] is None:
        wl_info["versions"][0]["workloadProperties"].pop("limit_memory")
    if wl_info["versions"][0]["workloadProperties"]["limit_CPUs"] is None:
        wl_info["versions"][0]["workloadProperties"].pop("limit_CPUs")

    # Handle Docker repo path
    if isinstance(wl_version_def.source, DockerRepoPath):
        wl_info["versions"][0]["dockerFileOption"] = "path"
        wl_info["versions"][0]["dockerFilePath"] = wl_version_def.source.path
        if wl_version_def.source.auth_credentials:
            wl_info["versions"][0]["auth_credentials"] = {
                "username": wl_version_def.source.auth_credentials.username,
                "password": wl_version_def.source.auth_credentials.password,
            }
        wl_info["versions"][0]["files"] = []
    elif isinstance(wl_version_def.source, UploadFile):
        raise ActionUnsuccessful("Uploading file not yet supported.")
    wl_info["versions"][0].pop("source")


def prepare_remote_connection_dict_from_wl_def(rc_def: RemoteConnection_Definition) -> dict:
    """Prepares a dictionary for remote connection definition.

    :param rc_def: The remote connection definition.
    :return: A dictionary with the remote connection details.
    """
    remote_connection_dict = asdict(rc_def)
    remote_connection_dict["headerType"] = rc_def.type
    remote_connection_dict["serviceName"] = ""
    return remote_connection_dict


def delete_workload_from_ms(_id: str, verbose: bool = False) -> str:
    """Deletes a workload from the management system.

    :param _id: The ID of the workload to delete.
    :param verbose: If True, prints additional information during execution.
    :return: The ID of the deleted workload.
    """
    response = make_request(f"/nerve/workload/{_id}", method="DELETE")
    if not response:
        raise ActionUnsuccessful(serverMessage(response))
    return _id
