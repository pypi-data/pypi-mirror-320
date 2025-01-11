import os, sys, subprocess
from abc import ABC, abstractmethod
from shared.constants import REQUIRED_MAJOR, REQUIRED_MINOR


class BaseOSManager(ABC):
    """Interface for OS-specific handlers."""
    #region Abstract Methods
    @abstractmethod
    def _create_virtual_environment(self):
        pass

    @abstractmethod
    def _activate_virtual_environment(self):
        pass

    @abstractmethod
    def _update_python(self, required_major, required_minor):
        pass

    @abstractmethod
    def _get_executable(self):
       pass
    #endregion
  
    #region NON Abstract Methods
    # Check Python Version
    def _check_python_version(self):
        # Specify the required version
        required_major = REQUIRED_MAJOR
        required_minor = REQUIRED_MINOR
        # Get the current Python version
        current_version = sys.version_info

        # Check if the current version matches the required version
        if current_version.major < required_major or (current_version.major < required_major and current_version.minor <= required_minor):
            print(f"You are using Python {current_version.major}.{current_version.minor}. This script requires Python {required_major}.{required_minor}. Attempting to update...")
            self._update_python(required_major, required_minor)
        else:
            print("Python is compatible")
            # tkinter.messagebox.showinfo("Version Check", f"Your Python version is {current_version.major}.{current_version.minor}. You're good to go!")

    def _install_requirements(self):
        try:
            if self._check_missing_packages().__len__() > 0:
                requirements = os.path.join(f"{os.getcwd()}", 'requirements.txt')
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements])
        except Exception as e:
            print(f"Error installing requirements {e}")

    def _check_missing_packages(self):
        try:
            req = os.path.join(f"{os.getcwd()}", 'requirements.txt')

            # Read requirements.txt and check for installed packages
            with open(req, 'r') as f:
                required_packages = {line.split('==')[0].strip().lower() for line in f if line.strip() and not line.startswith('#')}
        
            installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', "list"], text=True).splitlines()[2:]
            installed_packages = {line.split()[0] for line in installed_packages}

            # Find missing packages
            missing = required_packages - installed_packages
        except Exception as e:
            print(f"Error checking missing packages {e}")

        return missing
    
    # Public Method
    def initialize_dependencies(self):
        # Step 1: Check Python version
        self._check_python_version()

        # Step 2: Create virtual environment
        self._create_virtual_environment()

        # Step 3: Install Requirements
        self._install_requirements()
    #endregion