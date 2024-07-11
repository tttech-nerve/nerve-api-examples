from setuptools import setup

setup(
    name = "nerve-clt",
    version = "1.1.1",
    description = ("Linux command line tool to control a Nerver Management System."),
    packages=["nerve_clt"],
    python_requires=">=3.10",
    install_requires=[
        "nerve>=1.1.1",
    ],
    entry_points = {
        "console_scripts": ["nerve=nerve_clt.clt:main"]
    }
)
