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
"""This module provides an implementation for setting and storing login credentials for the Nerve management system.

It supports fetching credentials from various sources, including command-line arguments, environment variables,
credentials stored in a file, and user input.
Additionally, it attempts to login with these credentials and saves the session ID for further use.
This module is a part of the TTTech Industrial Automation AG's nerveapi package, intended to streamline the process of 
interacting with the Nerve management system.
"""
import os
import getpass
import validators

from nerveapi.session import (
    login,
    get_ms_version
)
from nerveapi.utils import (
    save_session_id,
    ActionUnsuccessful,
    load_credentials_from_file,
    save_credentials
)
from nerveapi.utils import append_ending, DataNotAsExpected


def handle_set_login(args):
    """Handles setting and storing login credentials for the Nerve management system.

    This function attempts to fetch login credentials from various sources in a prioritized order:
    1. Command-line arguments provided by the user.
    2. Environment variables set in the system.
    3. Credentials stored in a specified file.
    4. Direct user input if the above methods do not yield credentials.

    After obtaining the credentials, it attempts to log in to the Nerve management system. If successful, the session 
    ID is saved for future use. Additionally, the user is given the option to save these credentials for later use.

    Parameters:
    args (Namespace): An argparse Namespace object containing potential URL, username, and password among other 
    command-line arguments.

    Returns:
    None: The function primarily prints to console and saves session information, without returning any value.
    """
    # Try fetching credentials from command-line arguments
    url = None
    username = None
    password = None

    if args.url:
        url = args.url
    if args.username:
        username = args.username
    if args.password:
        password = args.password

    if url: 
        print("URL found in command-line arguments:", url)
    if username: 
        print("Username found in command-line arguments:", username)
    if password: 
        print("Password found in command-line arguments.")

    if not url and os.getenv('NERVE_URL'):
        url = os.getenv('NERVE_URL')
        print("URL found in environment variable:", url)

    if not username and os.getenv('NERVE_USERNAME'):
        username = os.getenv('NERVE_USERNAME')
        print("Username found in environment variables:", username)

    if not password and os.getenv('NERVE_PASSWORD'):
        password = os.getenv('NERVE_PASSWORD')
        print("Password found in environment variable.")

    if not url or not username or not password:
        try:
            filename = append_ending(args.file, ".ini")
            url_from_file, username_from_file, password_from_file = load_credentials_from_file(
                filename)

        except ActionUnsuccessful as e:
            url_from_file = None
            username_from_file = None
            password_from_file = None
            print(e)
        if not url and url_from_file:
            url = url_from_file
            print("URL found in file:", url)
        if not username and username_from_file:
            username = username_from_file
            print("Username found in file:", username)
        if not password and password_from_file:
            password = password_from_file
            print("Password found in file.")


    url = url if url else input("Enter the Nerve management system URL: ")
    url = url.rstrip('/')       # The MS doesnt like a slash.
    # add https:// if not present
    if not url.startswith("http"):
        url = "https://" + url

    prompted_for_username = False
    if not username:
        username = input("Enter your username: ")
        prompted_for_username = True

    prompted_for_password = False
    if not password:
        password = getpass.getpass("Enter your password: ")
        prompted_for_password = True

    if not validators.url(url): 
        print("Invalid URL provided.")
        return
    if not validators.email(username):
        print("Invalid username provided. Nerve usernames are email addresses.")
        return

    session_id = None
    try:
        session_id = login(url, username, password)
        save_session_id(session_id, url)
    except ActionUnsuccessful as e:
        print(f"Login failed: {e}")
        return

    print("Login successful.")

    # Save the credentials to a file if the user had to enter the PW and he wants to save it.
    if (prompted_for_password or prompted_for_username):
            # ask if the user wants to save the credentials
            if not args.yes: 
                save = input(f"Do you want to save the credentials in {filename} ? (y/n) ")
            else:
                save = "y"

            if save.lower() == "y":
                pw_to_save = password
                username_to_save = username
            else:
                pw_to_save = None
                username_to_save = None
            
            save_credentials(url, username_to_save, pw_to_save, filename)



    try:
        version = get_ms_version()
    except DataNotAsExpected as e:
        print(
            f"Warning: Could not determine the version of the management system. {e}")
        return
    except ActionUnsuccessful as e:
        print(f"Warning: Could not determine the version of the management system. {e}")
        return

    if (version not in ["2.8.0"]):
        print("")
        print("Warning: This tool was tested with version 2.8.0 of the Nerve management system."+
              " It may not work with other versions.")
        print("Your management system is running version", version, ".")

    print()
    print("Set login to", url, "with version", version, "as", username, ".")
