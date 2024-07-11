#!/bin/bash
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

# Prompt user for NERVE environment variables
read -p "Enter the Nerve management system URL: " nerve_url
read -p "Enter your Nerve username: " nerve_username
# Use -s flag with read command to hide password input
read -s -p "Enter your Nerve password: " nerve_password
echo -e "\n"  # Add a newline after password input

# Append the export commands to ~/.bashrc or another profile script
echo "export NERVE_URL='$nerve_url'" >> ~/.bashrc
echo "export NERVE_USERNAME='$nerve_username'" >> ~/.bashrc
echo "export NERVE_PASSWORD='$nerve_password'" >> ~/.bashrc

# Inform the user
echo -e "The environment variables have been added to your ~/.bashrc\n"
echo "Please run 'source ~/.bashrc' or restart your terminal to apply the changes."
