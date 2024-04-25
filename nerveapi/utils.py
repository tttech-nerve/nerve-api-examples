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
"""Miscellaneous utility functions."""

import configparser
import json
import re
import pprint


def save_credentials(url: str, username: str, password: str, filename: str = 'credentials.ini'):
    """Saves API credentials to a file.

    Parameters:
    - url: API URL.
    - username: API username.
    - password: API password.
    - filename: Filename for storing the credentials.
    """
    config = configparser.ConfigParser()
    config['Credentials'] = {}
    if url:
        config['Credentials']['url'] = url
    if username:
        config['Credentials']['username'] = username
    if password:
        config['Credentials']['password'] = password

    with open(filename, 'w') as configfile:
        config.write(configfile)


def load_credentials_from_file(filename: str = 'credentials.ini') -> tuple:
    """Loads API credentials from a file.

    Parameters:
    - filename: The name of the file from which to load the credentials.

    Returns:
    A tuple containing URL, username, and password. If the file or section is not found, returns (None, None, None).
    """
    config = configparser.ConfigParser()
    config.read(filename)
    url = None
    username = None
    password = None

    if 'Credentials' in config:
        url = config['Credentials'].get('url')
        username = config['Credentials'].get('username')
        password = config['Credentials'].get('password')
    return url, username, password


def load_session_id(filename: str = 'session_id.ini') -> tuple:
    """Loads the session ID from a file.

    Parameters:
    - filename: The name of the file from which to load the session ID.

    Returns:
    The session ID as a string, or None if not found.
    """
    config = configparser.ConfigParser()
    config.read(filename)
    if 'Session' in config:
        session_id = config['Session'].get('sessionid')
        base_url = config['Session'].get('baseurl')
        return (session_id,base_url)
    return (None,None)


def save_json(wl_info, filename: str):
    """Saves workload information to a file in JSON format.

    Parameters:
    - wl_info: A list of dictionaries containing workload information.
    - filename: The name of the file to save the information to.
    """
    with open(filename, 'w') as output_file:
        json.dump(wl_info, output_file, indent=4)


def load_json(filename: str):
    """Loads workload information from a file in JSON format.

    Parameters:
    - filename: The name of the file to load the information from.

    Returns:
    A list of dictionaries containing workload information.
    """
    with open(filename, 'r') as input_file:
        return json.load(input_file)


def save_session_id(session_id: str, base_url: str, filename: str = 'session_id.ini'):
    """Saves the session ID and the base URL to a file.

    Parameters:
    - session_id: The session ID to save.
    - base_url: The base URL to save.
    - filename: The name of the file to save the session ID to.
    """
    config = configparser.ConfigParser()
    config['Session'] = {'sessionid': session_id,
                            'baseurl': base_url}
    with open(filename, 'w') as configfile:
        config.write(configfile)


def create_regex(pattern: str) -> re.Pattern:
    """Creates a regex pattern from the given pattern string.

    Parameters:
    - pattern: The pattern string. Can be a regular expression or a plain string. If None, matches anything.

    Returns:
    A compiled regular expression object.
    """
    if pattern is None:
        regex_pattern = ".*"
    elif pattern.startswith("regex:"):
        regex_pattern = pattern[len("regex:"):]
    else:
        regex_pattern = r"\b" + re.escape(pattern) + r"\b"
    try:
        return re.compile(regex_pattern)
    except re.error as e:
        print(f"Ignoring invalid regex pattern: {regex_pattern}. Error: {e}")
        return re.compile(".*")


def append_ending(filename: str, ending: str) -> str:
    """Appends a specific ending to a filename if it doesn't already have that ending.

    Parameters:
    - filename: The original filename.
    - ending: The ending to append.

    Returns:
    The filename with the specified ending.
    """
    return filename if filename.endswith(ending) else filename + ending


def rename_dict_field(d: dict, old_field: str, new_field: str):
    """Renames a field in a dictionary.

    Parameters:
    - d: The dictionary whose field is to be renamed.
    - old_field: The current name of the field.
    - new_field: The new name of the field.
    """
    if old_field in d:
        d[new_field] = d.pop(old_field)


class ActionUnsuccessful(Exception):
    """Exception raised when an action is unsuccessful."""
    pass


class DataNotAsExpected(Exception):
    """Exception raised when the data is not as expected."""
    pass


def serverMessage(response) -> str:
    """Extracts a message from a server response object.

    Parameters:
    - response: The server response object.

    Returns:
    A string message extracted from the response.
    """
    try:
        if response is None:
            return "No response received."
        json_content = response.json()
        if isinstance(json_content, list) and json_content:
            first_item = json_content[0]
            if isinstance(first_item, dict):
                return first_item.get('message', "No message returned.")
        elif isinstance(json_content, dict):
            return json_content.get('message', "No message returned.")
    except ValueError:
        pass
    return "Server response: " + pprint.pformat(response)


def complainIfKeysAreNotInDict(d: dict, keys: list):
    """Checks if certain keys are present in a dictionary and raises an exception if not.

    Parameters:
    - d: The dictionary to check.
    - keys: A list of keys to check for in the dictionary.
    """
    missing_keys = [key for key in keys if key not in d]
    if missing_keys:
        raise DataNotAsExpected(
            f"Missing expected keys: {', '.join(missing_keys)}")



def complainIfNotAList(d, length=None):
    """Checks if The data is a list.

    Parameters:
    - d: The item to check.
    """
    if not isinstance(d, list):
        raise DataNotAsExpected(f"Expected a list, got {type(d)}")
    
    if length is not None and len(d) != length:
        raise DataNotAsExpected(f"Expected a list of length {length}, got {len(d)}")


def findDictByValue(d: list, key: str, value: str) -> dict:
    """Finds a dictionary in a list of dictionaries by a specific value.

    Parameters:
    - d: The list of dictionaries to search.
    - key: The key to search for.
    - value: The value to search for.

    Returns:
    The dictionary containing the specified value, or None if not found.
    """
    for item in d:
        if item.get(key) == value:
            return item
    return None
