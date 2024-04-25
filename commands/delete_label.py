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
"""Implementation of the delete label command."""

from nerveapi.labels import delete_label
from nerveapi.utils import ActionUnsuccessful

def handle_delete_label(args):
    """Implementation of the create_label command."""
    print("Labels operation are in beta stage.")

    try:
        delete_label(_id=args.id)
        print("Deleted")
    except ActionUnsuccessful as e:
        print("Failed to delete label.",e)
        return
