from setuptools.command.build_py import build_py
import os
from setuptools import setup, find_packages

# Define the Git repository URL and build directory
BUILD_DIR = os.path.join(os.path.dirname(__file__), "build")
OUTPUT_LIB_PATH = os.path.join(os.path.dirname(__file__),"pyamigamods", "songtools.so")

# Custom build command to clone and build the shared library
class CustomBuild(build_py):
    def run(self):
        if not os.path.exists(OUTPUT_LIB_PATH):
            build_utils.clone_and_build(BUILD_DIR, OUTPUT_LIB_PATH)
        build_utils.clone_and_build(BUILD_DIR, OUTPUT_LIB_PATH)
        super().run()


setup(
    name='pyamigamods',
    version='0.1',
    packages=find_packages("build_utils"),
    cmdclass={'build_py': CustomBuild},  # Use the custom build command
    install_requires=[],  # Add dependencies if needed
    include_package_data=True,  # Include the shared library in the package
    package_data={
        'pyamigamods': ['songtools.so'],  # Include the shared library
    },
)
