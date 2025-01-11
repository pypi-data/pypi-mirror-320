import os
import subprocess
import sys
import venv
from shared.constants import ENV_NAME, ENV_PATH
from .base_os_manager import BaseOSManager

class WindowsDependencyManager(BaseOSManager):
    def __init__(self):
        super().__init__()

    #TODO: rewrite to check for scripts folder
    def _create_virtual_environment(self):
        """Creates a Python virtual environment using the venv module."""
        try:
            if not os.path.exists(ENV_PATH):
                print(f"Creating virtual environment at {ENV_NAME}...")
                venv.create(ENV_NAME, with_pip=True)
                print("Virtual environment created successfully.")
            else:
                print("Environment is already created")

            self._activate_virtual_environment()
        except Exception as e:
            print(f"Failed to create virtual environment: {e}")
            sys.exit(1)

    def _activate_virtual_environment(self):
        print("Setting up virtual environment executable and packages")
        # Set the sys.executable to the Python executable inside the virtual environment
        sys.executable = self._get_executable("python")
        site_packages_path = ""
        site_packages_path = os.path.join(ENV_NAME, "lib", "site-packages")
        sys.path.append(ENV_NAME)
        sys.path.append(site_packages_path)
        print("Environment setup complete.")
    
    def _update_python(self, required_major, required_minor):
        # tkinter.messagebox.showinfo("Version Warning", f"Please download the installer from https://www.python.org/downloads/release/python-{required_major}{required_minor}0/")
        print(f"Please download the installer from https://www.python.org/downloads/release/python-{required_major}{required_minor}0/")
        subprocess.run(["start", f"https://www.python.org/downloads/release/python-{required_major}{required_minor}0/"], shell=True)

    def _get_executable(self, package):
        """Returns the Python executable path for the virtual environment."""
        return os.path.join(ENV_PATH, "Scripts", f"{package}.exe")

