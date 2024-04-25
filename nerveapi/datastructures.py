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
"""Datastructures for the workloads. The datastructures are separated out as reference for the Nerve API.

They hold the data necessary to create docker workloads in the Nerve API. They are coarsely aligned with the 
structures used by the API.
"""
#
from dataclasses import dataclass, field
from typing import List, Optional,  Union
from nerveapi.utils import DataNotAsExpected


# Data structures for the Nerve API
# The _definition classes hold all possible information that need to be sent to the MS for creating a new object.
# The dataclasses could be avoided alltogehter, but then it would be less clear which data needs to be stored.

# Workload

@dataclass
class PortMappingsProtocol:
    """Port definition."""
    container_port: int
    host_port: int
    protocol: str


@dataclass
class Selector:
    """Selector definition."""
    key: str
    value: str


@dataclass
class User_and_Date:
    """User and date definition."""
    user: str
    date: str


@dataclass
class LimitMemory:
    """Memory limit definition."""
    unit: str  # one of "GB", "MB"
    value: float


@dataclass
class Date_only:
    """Date definition."""
    date: str


@dataclass
class Volume:
    """Volume definition."""
    volumeName: str
    containerPath: str
    configurationStorage: bool


@dataclass
class EnvironmentVariable:
    """Environment variable definition."""
    env_variable: str
    container_value: str


@dataclass
class RemoteConnection_Definition:
    """Remote connection definition."""
    acknowledgment: str
    hostname: str
    localPort: int
    name: str
    port: int
    type: str


@dataclass
class Template:
    """Template definition."""
    values: List[str] = field(default_factory=list)


@dataclass
class UploadFile:
    """Upload file definition."""
    file_name: str


@dataclass
class AuthCrendentials:
    """Auth credentials definition."""
    username: str
    password: str

@dataclass
class DockerRepoPath:
    """Docker repo path definition."""
    path: str
    auth_credentials: Optional[AuthCrendentials] = None

@dataclass
class WorkloadVersion_Docker_Properties_Definition:
    """Workload version docker properties definition."""
    # port_mappsing_protocol
    environment_variables: List[EnvironmentVariable]
    limit_memory: LimitMemory
    container_name: str
    limit_CPUs: int
    restart_policy: str
    docker_volumes: List[Volume]
    networks: List[str]
    port_mappings_protocol: List[PortMappingsProtocol]


@dataclass
class WorkloadVersion_Docker_Definition:
    """Workload version docker definition."""
    name: str
    selectors: List[str]
    released: bool
    workloadProperties: WorkloadVersion_Docker_Properties_Definition
    restartOnConfigurationUpdate: bool
    remoteConnections: List[RemoteConnection_Definition]
#    firstVolumeAsConfigurationStorage: bool
    source: Union[UploadFile, DockerRepoPath]


@dataclass
class Workload_Definition:
    """Workload definition."""
    type: str
    name: str
    description: str
    versions: WorkloadVersion_Docker_Definition

# ------------------ Functions to create and parse data for the Nerve API ------------------


def create_remote_connection_definition_from_json(item):
    """Creates a RemoteConnection_Definition from the JSON returned by the Nerve API.

    Parameters:
    - item (dict): The dictionary containing the remote connection data.

    Returns:
    - RemoteConnection_Definition: An instance populated with the data from 'item', or None if 
      the type is unsupported or 'item' is None.

    Raises:
    - DataNotAsExpected: If the type of the remote connection is not supported.
    """
    if not item:
        return None
    if item.get('type') != "TUNNEL":
        raise DataNotAsExpected(f"Remote Connection type {item.get('type')} not supported yet.")

    return RemoteConnection_Definition(
        acknowledgment=item.get("acknowledgment"),
        hostname=item.get("hostname", ""),
        localPort=item.get("localPort"),
        name=item.get("name"),
        port=item.get("port"),
        type=item.get("type")
    )


def create_workload_version_definition_from_json(item, type):
    """Creates a WorkloadVersion_Docker_Definition from the JSON returned by the Nerve API.

    Parameters:
    - item (dict): The dictionary containing the workload version data. May be None, in which case, None is returned.
    - type (str): The type of the workload.

    Returns:
    - RemoteConnection_Definition: An instance populated with the data from 'item', or None if 
      the type is unsupported or 'item' is None.

    Raises:
    - DataNotAsExpected: If something is not supported or data is unexptected.

    """
    if not item:
        return None

    source = item.get("source")

    if "file_name" in source:
        source = UploadFile(file_name=source.get("file_name"))

    elif "path" in source:
        acd = source.get("auth_credentials", None)
        if acd:
            source = DockerRepoPath(
                path=source.get("path"),
                auth_credentials=AuthCrendentials(
                    username=acd.get("username"),
                    password=acd.get("password")
                )
            )
        else:
            source = DockerRepoPath(path=source.get("path"))

    remoteConnections = []
    for rc in item.get("remoteConnections"):
        rcd = create_remote_connection_definition_from_json(rc)
        if rcd:
            remoteConnections.append(rcd)

    selectors = item.get("selectors")
    if len(selectors) > 0:
        print("Selectors are not supported yet. Omitting.")

    lm_def = item.get("workloadProperties").get("limit_memory", None)
    limit_memory = LimitMemory(** lm_def) if lm_def else None

    pmp_def = item.get("workloadProperties").get("port_mappings_protocol", [])
    pmp = [PortMappingsProtocol(**item) for item in pmp_def]

    if type == "docker":
        return WorkloadVersion_Docker_Definition(
            released=item.get("released"),
            selectors=[],
            remoteConnections=remoteConnections,
            restartOnConfigurationUpdate=item.get(
                "restartOnConfigurationUpdate"),
            #                    firstVolumeAsConfigurationStorage= item.get("firstVolumeAsConfigurationStorage"),
            name=item.get("name"),
            workloadProperties=WorkloadVersion_Docker_Properties_Definition(
                environment_variables=[EnvironmentVariable(
                    **item) for item in item.get("workloadProperties").get("environment_variables", [])],
                limit_memory=limit_memory,
                container_name=item.get(
                    "workloadProperties").get("container_name"),
                limit_CPUs=item.get("workloadProperties").get(
                    "limit_CPUs", None),
                restart_policy=item.get("workloadProperties").get(
                    "restart_policy", ""),
                docker_volumes=[Volume(
                    **item) for item in item.get("workloadProperties").get("docker_volumes", [])],
                networks=item.get("workloadProperties").get("networks", []),
                port_mappings_protocol=pmp,
            ),
            #                    dockerFilePath= item.get("dockerFilePath"),
            #                    dockerFileOption= item.get("dockerFileOption"),
            #                    files= item.get("files")
            source=source
        )
    else:
        print(f"Type {type} not supported yet.")
        return None


def create_workload_definition_from_json(json_data):
    """Creates a Workload_Definition from the JSON returned by the Nerve API."""
    if not json_data:
        return None
    versions = []
    type = json_data.get("type")
    if type == "docker":
        for item in json_data.get("versions"):
            versions.append(
                create_workload_version_definition_from_json(item, type))
    else:
        raise DataNotAsExpected(f"Type {type} not supported yet.")
    
    return Workload_Definition(
        type=type,
        name=json_data.get("name"),
        description=json_data.get("description"),
        versions=versions
    )
