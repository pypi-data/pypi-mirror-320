from setuptools import setup

setup(
    name="datdeptrai",  # Name of your CLI tool
    version="1.0.0",
    py_modules=["cli"],  # Reference the cli.py file (without the .py extension)
    install_requires=[
        "click",  # Ensure dependencies are installed
    ],
    entry_points={
        "console_scripts": [
            "dat=cli:cli",  # Command name=module:function
        ],
    },
)