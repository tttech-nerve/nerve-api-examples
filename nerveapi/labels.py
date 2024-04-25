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
"""Handling of labels."""

from .session import make_request
from .utils import (
    complainIfNotAList,
    complainIfKeysAreNotInDict,
    ActionUnsuccessful,
    serverMessage
)
from json import JSONDecodeError

def create_label(key: str, value: str):
    """Creates a label in the system with the specified key and value.

    Parameters:
    - key: The key of the label.
    - value: The value of the label.

    This function sends a POST request to create a new label and prints the outcome.
    """
    # Prepare the payload with the label details. Some fields like '_id' and timestamps are managed by the server.
    data = {
        "_id": "",
        "key": key,
        "value": value,
        "createdAt": "",
        "transformed": ""
    }

    # Send the POST request to the server to create the label.
    response = make_request('/nerve/labels', method='POST', data=data)

    if not response:
        raise ActionUnsuccessful(serverMessage(response))
    # Check the response and print the outcome.


def get_labels():
    """Returns a dictionary of labels, where the id is the key and the value is a tuple (key,value)."""
    result = make_request("/nerve/labels/list")
    try:
        data = result.json()
    except JSONDecodeError:
        raise ActionUnsuccessful("Could not decode JSON response.")
    complainIfKeysAreNotInDict(data, ["count", "data"])
    label_list = data.get("data")

    labels = {}
    for label in label_list:
        complainIfKeysAreNotInDict(label, ["key", "value", "_id"])
        labels[label["_id"]] = (label["key"], label["value"])
    return labels


def delete_label(_id: str):
    """Deletes the label with the specified id.

    Parameters:
    - _id: The id of the label to delete.

    This function sends a DELETE request to remove the label and prints the outcome.
    """
    response = make_request(f"/nerve/labels/{_id}", method='DELETE')

    if not response:
        raise ActionUnsuccessful(serverMessage(response))
    # Check the response and print the outcome.
    return