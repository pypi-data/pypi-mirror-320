This is a project to auto install package dependencies into a virtual environment by reading a requirements.txt file.

Example call factory
# Import the package
from auto-package-installer.factory import OSDependencyManagerFactory

# Get the Handler
handler = OSDependencyManagerFactory.get_handler()
# Call the initializ_dependencies giving it the python major and minor values
handler.initialize_dependencies(3, 12)
