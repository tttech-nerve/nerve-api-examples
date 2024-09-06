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
"""Implementation of the logout command."""

from nerveapi.session import logout
from nerveapi.utils import ActionUnsuccessful
from commands.utils import eprint


def handle_logout(args) -> int:
    """Handles the user logout process and optionally clears saved credentials.

    This function attempts to log the user out of the session. If the user has specified not to keep the credentials
    (through the --keep_credentials flag being False), it will also clear the saved credentials.

    Parameters:
    - args: Argparse arguments, expected to include a 'keep_credentials' attribute 
    indicating whether to retain or clear stored credentials.

    Returns:
    - int: The exit code to return to the shell. 0 indicates success, while any other value indicates an error.
    """
    try:
        # Attempt to log out from the current session.
        logout()
        print("Logged out.")
        return 0
    except ActionUnsuccessful as e:
        # If logout fails (e.g., due to a lost connection or session timeout), print the error.
        eprint(f"Logout failed: {e}")
        return 1

