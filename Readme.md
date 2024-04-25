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

## Use as Library

The API functions require one commonly held state which is the session id after login. The session is stored in session_id.ini in the file system. This was done to avoid handing the state through all calls.
All API functions make extensive use of exceptions to inform the user about unforeseen problems in the call. Make sure to expect those.
