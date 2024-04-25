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
"""Session handling."""

import requests
from nerveapi.utils import (
    load_session_id, 
    save_session_id, 
    complainIfKeysAreNotInDict,
    complainIfNotAList, 
    serverMessage,
    ActionUnsuccessful
)
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder



def login(base_url, identity, secret):
    """Attempt to log in to the Nerve management system.

    Parameters:
    - url: The base URL of the Nerve management system.
    - identity: The user's identity (e.g., email).
    - secret: The user's password.

    Returns:
    - The session ID if login is successful; None otherwise.
    """
    #
    login_url = f"{base_url}/auth/login"
    payload = {'identity': identity, 'secret': secret}

    try:
        response = requests.post(login_url, json=payload)
    except requests.exceptions.MissingSchema:
        raise ActionUnsuccessful(
            "Invalid URL provided. URLs must start with http:// or https://.") from None
    except requests.exceptions.ConnectionError:
        raise ActionUnsuccessful(
            "Failed to connect to the server. Please check your network connection.") from None

    if response.status_code == 200:
        session_id = response.json().get('user').get('sessionId')
        save_session_id(session_id, base_url)
        return session_id
    
    elif response.status_code == 403:
        raise ActionUnsuccessful("Invalid credentials provided.")
    else:
        raise ActionUnsuccessful("Server responded:" + serverMessage(response))


def logout():
    """Attempt to log out of the Nerve management system by sending a logout request.

    This function does not take any parameters. It uses a previously stored session ID to authenticate the logout 
    request. If the logout is successful, it will clear the stored session ID and logout from the MS.

    Raises:
    - ActionUnsuccessful: If the server returns a response indicating that the logout operation was unsuccessful.

    Returns:
    - None
    """
    #
    try:
        make_request("/auth/logout", method='POST')
    except ActionUnsuccessful:
        raise ActionUnsuccessful("Logout failed. Maybe you are not logged in.") from None

    save_session_id('', '')


def make_request(endpoint, method='GET', data=None, files=None, workaround=None):
    """Makes an authenticated request to the specified endpoint of the Nerve management system.

    Parameters:
    - endpoint: The endpoint to make the request to (e.g., '/api/data').
    - method: The HTTP method to use (e.g., 'GET', 'POST').
    - data: The data to send in the request (applicable for POST requests).
    - files: The files to send in the request (applicable for multipart/form-data POST requests).
    - workaround: Injects the session ID into the data as SessionToken, if "Inject_Session_Token_To_Controller_Call" 
      is given. This is a workaround to avoid the need of putting the sessionId in the operative level of the function
      calls.

    Returns:
    - The response from the server.
    """
    #
    (session_id, base_url) = load_session_id()
    if not session_id or not base_url:
        raise ActionUnsuccessful("Please log in.")
    

    headers = {'sessionId': session_id,
               'Sec-Fetch-Dest': 'empty',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Site': 'same-origin'
               }

    url = f"{base_url}{endpoint}"

    if workaround:
        if workaround == "Inject_Session_Token_To_Controller_Call":
            if data:
                data["sessionToken"] = session_id
        else:
            raise ActionUnsuccessful(f"Unknown workaround: {workaround}")

    def send_request(headers, data=None, files=None):
        if files:
            fields = {}
            if data:
                # Omit filename for JSON part
                fields['data'] = ('', json.dumps(data), 'application/json')
            for key, file_content in files.items():
                fields[key] = file_content  # Add files to the request

            m = MultipartEncoder(fields=fields)
            # Set the correct content-type for the multipart request
            headers['Content-Type'] = m.content_type
            body = m
            return requests.request(method, url, headers=headers, data=body)
        else:
            if data:
                # Explicitly set Content-Type for JSON data
                headers['Content-Type'] = 'application/json'
                data = json.dumps(data)
            return requests.request(method, url, headers=headers, data=data)

    # Attempt to send the initial request
    response = send_request(headers, data, files)

    # Check if the session ID was invalid or expired
    if response.status_code == 401:
        print("Session does not work anymore. Please log-in.")

    return response


def get_ms_version():
    """Retrieves the  version of the Nerve management system from the cloud.

    This function makes an authenticated request to the Nerve management system's update endpoint and returns 
    the current version.

    Raises:
    - ActionUnsuccessful: If the server's response does not include the expected 'version' key in the data.
    - DataNotAsExpected: If the server's response is not a list, indicating an unexpected format of the data.

    Returns:
    - str: The version of the MS. or None if the list could not be retrieved.
    """
    result = make_request('/nerve/update/cloud/current-version')
    data = result.json()
    
    complainIfKeysAreNotInDict(data, ["currentVersion"])

    return data["currentVersion"]


# Example usage
if __name__ == "__main__":
    response = make_request("/nerve/v2/workloads")
    if response:
        print("Request Successful: ", response.status_code)
        print(response.json())  # Assuming the response is in JSON format
    else:
        print("Request Failed.")
