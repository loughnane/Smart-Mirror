Debian likes to control what's installed on the system so stuff like "pip install" doesn't work.

The way to handle this is to use "Virtual Environments". This means you can install one set of libraries for one project and another set of libraries for another.

To do it, go into the directory of your project and run the command `python3 -m venv .`. This will create a virtual environment for your project.

To activate the virtual environment you go into the directory and run `source bin/activate`

To deactivate, just enter the command `deactivate`
