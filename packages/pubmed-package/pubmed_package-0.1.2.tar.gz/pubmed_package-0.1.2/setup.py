from setuptools import setup, find_packages

with open("README.md", "r") as file:
    description = file.read()

setup(
    name='pubmed_package',
    version='0.1.2',
    packages=find_packages(),
    entry_points={
        "console_scripts":{
            "pubmed_api=pubmed:main",
        }
    },
    long_description =description,
    long_description_content_type="text/markdown",
)