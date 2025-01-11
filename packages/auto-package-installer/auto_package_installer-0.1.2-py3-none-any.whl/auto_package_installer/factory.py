import platform
from .linux_dependency_manager import LinuxDependencyManager
from .windows_dependency_manager import WindowsDependencyManager

class OSDependencyManagerFactory:
    @staticmethod
    def get_handler():
        """Return the appropriate handler based on the operating system."""
        os_name = platform.system().lower()
        if "linux" in os_name:
            return LinuxDependencyManager()
        elif "windows" in os_name:
            return WindowsDependencyManager()
        
        #TODO: Implement macOS
        # elif "darwin" in os_name:  # macOS
        #     return initialize_dependencies()
        else:
            raise NotImplementedError(f"Unsupported OS: {platform.system()}")