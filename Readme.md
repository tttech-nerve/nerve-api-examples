# Nerve API Example Scripts

## Description

This repository holds the examples to demonstrate the Nerve API and a command line tool based on the API. 

## Installation

These scripts have been developed and tested with Python 3.12 and it is recommended to run them with Python 3.12 or later. If you run the scripts with an older version of Python adaptations might be necessary. It is recommended to run the scripts within a virtual environment:


Create a new virtual environment called n_venv (or anything else you like) using your desired python version:
```
python3.12 -m venv n_venv
```

Activate the environment and check the Python version
```
source n_venv/bin/activate
python3 --version
```

Install the dependencies.
```
pip install -r requirements.txt
```

Check if everything works as intended.
```
python3 ./nerve.py --help
```


When you are done you can deactivate the environment.
```
deactivate
```


## License

The source code is released under MIT license (see the LICENSE file).

# Command line use and use as a library

The repository contains two parts;
The *commands* directory contains the functions for executing interactively from the command line.
The *nerveapi* directory contains the python module which encapsulates the api.
The individual Python files are structured along the objects they work on. To accomplish a specific task using the API functions, looking into the implementation of the corresponding command in the commands directory may be a good starting point.


## Command line use

Start the function running nerve.py with arguments. See --help for usage details.

As the helpfile to nerve.py states, the credentials may be provided in three different ways: as an environment variable, in a file or per command line prompt. 
Check the *set_login_environment_vars.sh* script to understand the naming of the variables.

### Example Usage

The main entry point for the command line is the `nerve.py` script. Run `python nerve.py --help` to get detailed information about all available commands.

Before any of the commands can be run on a management system, one needs to login. There are several ways to provide credentials. One way is to run the `set_login` command and provide the credentials and the Management System URL interactively:

```bash
python nerve.py set_login
# provide the requested information
```

When running the command, a login will be performed and the session information will be stored in the `session_id.ini` file. To logout one can either run the `python nerve.py logout` command. If you delete the `session_id.ini` file, a new login will be required.

Now we can perform operations on the Management system like e.g. listing all the docker workloads that are available on the management system:

```bash
python nerve.py list_workloads --type docker --output workloads.json --human
# this will write the result into the json file workloads.json and also print it to the command line in a human readable way
```
For more details about the command check the help `python nerve.py list_workloads --help`.

Another use case might be to get a list of all nodes where a specific workload version is currently deployed:
```bash
# list all nodes where workload with name 'nginx' is deployed in version 'v1' and save output also as json in 'nodes.json'
python nerve.py list_nodes -wn nginx -vn v1 --human --file nodes.json
```

The scripts also provide a workflow to create a new workload. Simply define the workload via a `json` file. To make it easier to create such a file, a template can be created from an existing workload:
```bash
# to create a docker workload first fetch a json file that contains such workload definitions from existing workloads on the management system
python nerve.py list_workloads --type docker --output workloads.json
# now take the first workload from that query and create a template from it for the new workload to be created
python nerve.py create_wl_template --input_file workloads.json --output_file wl_def.json
# now open the wl_def.json file with a text editor and adjust it to your needs to represent the new workload to be created and save it e.g. as 'new_wl.json'
# after that the new workload can be created on the Management System
python nerve.py create_workload --template new_wl.json
```

## Use as Library

The API functions require one commonly held state which is the session id after login. The session is stored in session_id.ini in the file system. This was done to avoid handing the state through all calls.
All API functions make extensive use of exceptions to inform the user about unforeseen problems in the call. Make sure to expect those.
