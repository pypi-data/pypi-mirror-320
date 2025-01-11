from setuptools import setup, find_packages

with open("README.md", "r") as file:
    description = file.read()

setup(
    name='pubmed_package',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'requests>=2.32'
    ],
    entry_points={
        "console_scripts":{
            "pubmed_api=pubmed:main",
        }
    },
    long_description =description,
    long_description_content_type="text/markdown",
)