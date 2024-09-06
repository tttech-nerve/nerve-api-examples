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
"""Main Command Line Interface."""

import argparse
from commands.set_login import handle_set_login
from commands.logout import handle_logout
from commands.list_workloads import handle_workloads_list 
from commands.create_workload import handle_create_workload
from commands.create_label import handle_create_label
from commands.get_labels import handle_get_labels
from commands.delete_label import handle_delete_label
from commands.delete_workload import handle_delete_workload
from commands.create_wl_template import handle_create_wl_template
from commands.list_nodes import handle_list_nodes
from commands.reboot_nodes import handle_reboot_nodes
from commands.control_workloads import (
    handle_start_workloads,
    handle_stop_workloads,
    handle_restart_workloads
)
import sys
from argparse import RawTextHelpFormatter

help_text = """
Nerve Management System CLI
available commands:
  set_login
  login
  logout

use 'nerve <command> --Help' for more information about a command.  
"""

description = """
Nerve Management System CLI

This is a command line interface for the Nerve Management System. It relies on files or environment variables to hold the credentials and a temporary file to hold the session information, as well as the workload list or node list. So the first thing you need to do is to set the login credentials with the set_login command, or set the environment variables using the shell script provided. For convinience, if you want to use different logins, you can use the set_login with a file name. 
Then you can use the other commands.

The delete_workload and create_wl_template commands rely on a workload list file, which can be created with the list_workloads command. So if you want to delete a list of workloads, first use list_workloads to create a list file, then use delete_workload to delete the workloads from the list file. The list of workloads created by the system contains the full workload information. However, to delete a workload, only the workload ID is needed.


The same holds for the start/stop/restart workload commands. The input file to the command specifies for which workloads the command will the executed.  So first, you usually would use the list_node command to create a list file, then use the start/stop/restart command to start/stop/restart the workloads from the list file. Consider that list_node per default adds to the node list. Use --new to create a new file instead of adding to the existing one.

The create_wl_template command helps you to create a json file that can be used as a template for creating a new workload in the MS. It takes the first workload from the list file and creates a json file that can be used as a template for creating a new workload in the MS. You can manually modify this file and use it as input for the create_workload command. Then you can use the create_workload command to create a new workload in the MS.


Most filters support regex. In order to use regex, use "regex:" as a prefix to the pattern. For example, to filter by type using a regex pattern, use "--type regex:pattern". Often you may want to put the whole filter in quotes, to avoid the shell interpreting the regex characters. For example, to filter by workload_name containing "new" using a regex pattern, use --name "regex:.*new".

Have fun!
"""

node_list_description = """
List nodes filtered by the criteria and store it into a node list or print the result.\n

When working on large systems, be aware that the command needs to anaylse every node which is not filtered out by the node filters. This can take a while if there are many nodes in the system. 

The node path is created from the folder names separated with '/'. The path starts with 'root'. Your filter needs to match this path if given. This may look like "root/Unassigned" or "root/folder1/subfolder".

The strings to match labels and their values are created like so: key:value. If you filter for a label, your filter string or regex has to match this pattern. For example, to filter any node with a label "location" containing "Berlin", use --node_labels "regex:location:.*Berlin".

If no filter for workloads is given, also nodes with no workloads are included in the result, otherwise only those nodes are included where the workload filters also match.

For matching the workload states, possible options are:
IDLE, CREATING, REMOVING, SUSPENDING, SUSPENDED, STARTING, RESTARTING, RESUMING, STARTED, STOPPING, STOPPED, ERROR, REMOVING_FAILED, PARTIALLY_RUNNING

The commands reboot, start, stop and restart rely on a node list file. You can create this file yourself or use the list_nodes command to create it. The commands will then use the file to execute the action on the nodes in the file.
When you create the file yourself, you can omit most information which is given in the node list file. You need to specify either the name or the serial number of a node to identify it. For a workload you either need the workload name, id or a version name.
 """

def main():
    """Main function to handle the command line interface."""
    #
    parser = argparse.ArgumentParser(description=description, prog="nerve", formatter_class=RawTextHelpFormatter)
    subparsers = parser.add_subparsers(required=True, help='Available sub-commands:')

    # Set login credentials
    parser_set_login = subparsers.add_parser('set_login', 
        help='Checks and sets login credentials. Uses file, enviroment vars or propmt.')
    parser_set_login.add_argument("-f", "--file", default="credentials.ini", 
        help="Take the file and use it to get the credentials. '.ini' is automatically appended.")
    parser_set_login.add_argument("-u", '--url', 
        help='Enter the Nerve Management System URL. "https://" is added if the url does not start with "http".')
    parser_set_login.add_argument("-un",'--username', help='Enter your username.')
    parser_set_login.add_argument("-pw",'--password', help='Enter your password.')
    parser_set_login.add_argument("-y",'--yes', help='Don\'t ask for confirmation.', action="store_true")
    parser_set_login.set_defaults(func=handle_set_login)

    # Log out
    parser_logout = subparsers.add_parser('logout', help='Log out and delete session data.')
    parser_logout.set_defaults(func=handle_logout)

    # List workloads
    parser_workloads_list = subparsers.add_parser('list_workloads', help="List workloads and store them.", 
                                                  description='List workloads with given filters. '+
                                                  'Store the result in a file or just print it as human readable text.')
    parser_workloads_list.add_argument("-t", '--type', 
                                       help='Exactly match type, typically docker|codesys|vm|docker-compose.')
    parser_workloads_list.add_argument("-V", '--verbose', 
                                       help='Show debug information.', action="store_true")
    parser_workloads_list.add_argument("-n", '--name', 
                                       help='Filter by name, supports regex.')
    parser_workloads_list.add_argument('--id', 
                                       help='Filter by ID, supports regex.')
    parser_workloads_list.add_argument("-H", '--human', 
                                       help='Return a listing instead of JSON.', action="store_true")
    parser_workloads_list.add_argument("-d", '--disabled', 
                                       help='Include disabled workloads in the results.', action="store_true")
    parser_workloads_list.add_argument("-v", '--version_name', help='Filter by version name, supports regex.')
# parser_workloads_list.add_argument('--version_id', help='Filter by version ID, supports regex.') TODO support as well
    parser_workloads_list.add_argument("-o",'--output', default="workloads.json", 
                                       help='Specify the output file name. Defaults to "workloads.json" if omitted.'+
                                        ' ".json" is appended if not included.')
    parser_workloads_list.set_defaults(func=handle_workloads_list)

    # Create workload
    parser_create_workload = subparsers.add_parser( 'create_workload', 
                                            description="Create a new workload from the input (template) file given.", 
                                            help='Create a new workload.')
    parser_create_workload.add_argument("-t",'--template', default="wl_def.json", 
                                        help='Template file name. Defaults to "wl.json" if omitted.')
    parser_create_workload.add_argument("-s",'--sequential', 
                                        help='Wait for completion of each download before starting a new one.', 
                                        action="store_true")
    parser_create_workload.add_argument("-V", '--verbose', help='Show debug information.', action="store_true")
    parser_create_workload.set_defaults(func=handle_create_workload)

    # Create label
    parser_create_label = subparsers.add_parser('create_label', help='Create a new label.')
    parser_create_label.add_argument("-k",'--key', required=True, help='Enter the key.')
    parser_create_label.add_argument("-v", '--value', required=True, help='Enter the value.')
    parser_create_label.set_defaults(func=handle_create_label)

    # Get label
    parser_create_label = subparsers.add_parser('get_labels', help='List the labels in the system.')
    parser_create_label.set_defaults(func=handle_get_labels)

    parser_delete_label = subparsers.add_parser('delete_label', help='Delete a label.')
    parser_delete_label.add_argument("--id", help='Enter the label ID.')
    parser_delete_label.set_defaults(func=handle_delete_label)

    parser_create_workload_definition_template = subparsers.add_parser('create_wl_template', 
            description="Creates a workload defintion template from the first workload in the workload list.", 
            help="Creates a workload defintion template from the first workload in the workload list.")
    parser_create_workload_definition_template.add_argument("-i",'--input_file', default="workloads.json", 
            help='Filename or blank for "workloads.json". The .json ending is automatically appended if not provided.')
    parser_create_workload_definition_template.add_argument("-o", '--output_file', default="wl_def.json", 
            help='Filename or blank for "wl_def.json". The ".json" ending is automatically appended if not provided.')
    parser_create_workload_definition_template.add_argument("-V", '--verbose', help='Show debug information.', 
            action="store_true")
    parser_create_workload_definition_template.set_defaults(func=handle_create_wl_template)

    # Delete workload
    parser_delete_workload = subparsers.add_parser('delete_workloads', 
            help='Delete workloads from a workload list file. Use list_workloads to create a list file.')
    parser_delete_workload.add_argument("-i", '--input_file', default="workloads.json", 
            help='Filename or blank for "workloads.json". The ".json" ending is appended if not provided.')
    parser_delete_workload.add_argument("-V", '--verbose', help='Show debug information.', action="store_true")
    parser_delete_workload.add_argument("-y",'--yes', help='Don\'t ask for confirmation.', action="store_true")

    parser_delete_workload.set_defaults(func=handle_delete_workload)

    # List Nodes

    parser_list_nodes = subparsers.add_parser( 'list_nodes', 
            help="List nodes and create a node list or add to the list. See the functions help for more information.", 
            description=node_list_description, formatter_class=RawTextHelpFormatter)
    parser_list_nodes.add_argument("-f", '--file_name', default="nodes.json", 
            help="File containing the node list, 'nodes.json' if left unspecified. "+
             " '.json' is added automatically if not specified")
    parser_list_nodes.add_argument("-a", '--add', 
            help="Add to the file instead creating a new one.", action="store_true")
    parser_list_nodes.add_argument("-nn",'--node_name', 
            help="Filter by node name, supports regex.")
    parser_list_nodes.add_argument("-np",'--node_path', 
            help="Filter by node path, supports regex. The path starts with 'root' and contains the folder " +
            "names separated with '/'")
    parser_list_nodes.add_argument("-nv", '--node_version', help="Filter by node version, supports regex.")
    parser_list_nodes.add_argument("-nm",'--node_model', help="Filter by node model, supports regex.")
    parser_list_nodes.add_argument("-nl", '--node_labels', help="Filter by node labels, supports regex.")
    parser_list_nodes.add_argument("-wn", '--workload_name', help="Filter by workload name, supports regex.")
    parser_list_nodes.add_argument("-wid",'--workload_id', help="Filter by workload ID, supports regex.")
    parser_list_nodes.add_argument("-vn",'--workload_version_name', 
            help= "Filter by workload version name, supports regex.")
    parser_list_nodes.add_argument("-vid",'--workload_version_id', 
            help="Filter by workload version ID, supports regex.")
    parser_list_nodes.add_argument("-ws",'--workload_status', 
            help="Filter by workload status, supports regex. See above for possible values.")
    parser_list_nodes.add_argument("-wt",'--workload_type', 
            help='Filter by workload type, supports regex. Typically Docker|Codesys|VM|"Docker Compose"')
    parser_list_nodes.add_argument("-V", '--verbose', help='Show debug information.', action="store_true")
    parser_list_nodes.add_argument("-H", '--human', 
            help='Print a listing instead of JSON. The resulting list is not written to a file.', action="store_true")
    parser_list_nodes.set_defaults(func=handle_list_nodes)

    parser_reboot_nodes = subparsers.add_parser('reboot_nodes', 
            help="Reboot nodes from a node list file.  See list_nodes help for details.")
    parser_reboot_nodes.add_argument("-f", '--input_file', default="nodes.json", 
            help='Filename or blank for "nodes.json". The ".json" ending is automatically appended if not provided.')
    parser_reboot_nodes.add_argument("-V", '--verbose', help='Show debug information.', action="store_true")
    parser_reboot_nodes.add_argument("-y", '--yes', help='Don\'t ask for confirmation.', action="store_true")    
    parser_reboot_nodes.set_defaults(func=handle_reboot_nodes)

    parser_start_workloads = subparsers.add_parser('start', 
            help="Start workloads from a workload list file.  See list_nodes help for details.")
    parser_start_workloads.add_argument("-f", '--input_file', default="nodes.json", 
            help='Filename or blank for "nodes.json". The ".json" ending is automatically appended if not provided.')
#  parser_start_workloads.add_argument("-v", '--verify', help='Verify the workloads after the action. 
#  Use with a time value in seconds, otherwise 15 seconds are assumed', nargs="?", type=int, const=15, 
# default=argparse.SUPPRESS, action="store")
    parser_start_workloads.add_argument("-V", '--verbose', help='Show debug information.', action="store_true")
    parser_start_workloads.set_defaults(func=handle_start_workloads)

    parser_stop_workloads = subparsers.add_parser('stop', 
            help="Stop workloads from a workload list file. See list_nodes help for details.")
    parser_stop_workloads.add_argument("-f", '--input_file', default="nodes.json", 
            help='Filename or blank for "nodes.json". The ".json" ending is automatically appended if not provided.')
    parser_stop_workloads.add_argument("-ff", '--force', help='Force stop the workloads.', action="store_true")
#   parser_stop_workloads.add_argument('--verify', help='Verify the workloads after the action. Use with a time value
#  in seconds, otherwise 15 seconds are assumed', nargs="?", type=int, const=15, default=argparse.SUPPRESS,
#  action="store")
    parser_stop_workloads.add_argument("-V", '--verbose', help='Show debug information.', action="store_true")
    parser_stop_workloads.set_defaults(func=handle_stop_workloads)

    parser_restart_workloads = subparsers.add_parser('restart', 
            help="Restart workloads from a workload list file.  See list_nodes help for details.")
    parser_restart_workloads.add_argument("-f", '--input_file', default="nodes.json", 
            help='Filename or blank for "nodes.json". The ".json" ending is automatically appended if not provided.')
# parser_restart_workloads.add_argument("-v",'--verify', help='Verify the workloads after the action. 
# Use with a time value in seconds, otherwise 15 seconds are assumed', nargs="?", type=int, const=15, default=argparse.
# SUPPRESS, action="store")
    parser_restart_workloads.add_argument("-V", '--verbose', help='Show debug information.', action="store_true")
    parser_restart_workloads.set_defaults(func=handle_restart_workloads)


    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    exit(args.func(args))


if __name__ == "__main__":
    main()
