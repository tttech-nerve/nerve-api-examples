from setuptools import setup

setup(
    name = "nerve",
    version = "1.1.1",
    description = ("Python bindings for the Nerve Management System API."),
    packages=["nerve"],
    python_requires=">=3.10",
    install_requires=[
        "iniconfig==2.0.0",
        "requests==2.31.0",
        "requests-toolbelt==1.0.0",
        "urllib3==2.2.1",
        "validators==0.24.0",
    ],
)
