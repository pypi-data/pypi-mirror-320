from setuptools import setup, find_packages

# Read the long description from your README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='indigen',
    version='0.1.1',  # Increment the version number
    packages=find_packages(include=["indigen", "indigen.*"]),  # Automatically find submodules
    include_package_data=True,
    author="Sudeep Ghate",
    author_email="sudeep1129@gmail.com",  # Add a valid email
    description="A package for generating synthetic names based on Indian states.",
    long_description=long_description,  # Add this line
    long_description_content_type="text/markdown",  # Specify that it's markdown
    url="https://github.com/ghatesudi/indigen",  # Add a valid project URL
    entry_points={
        "console_scripts": [
            "indigen=indigen.scripts.indigen:main",  # Reference your script's main function
        ],
    },
)
