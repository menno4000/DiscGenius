import os

from setuptools import setup, find_packages, find_namespace_packages
import unittest


def get_requirements():
    req_file = os.path.join(os.getcwd(), "requirements.txt")
    if not (os.path.exists(req_file) and os.path.isfile(req_file)):
        return []

    with open(req_file, "r") as f:
        return f.read().splitlines()


def get_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("test", pattern="test_*.py")
    return test_suite


if __name__ == "__main__":
    setup(
        name="discgenius",
        version="0.1",
        description="An Application for mixing Audio Files (i.e. songs) together by matching their tempo and beat placements.",
        packages=find_packages(),
        entry_points={
            "console_scripts": [
                "cme = cme.cli:main",
            ]
        },
        test_suite="setup.get_test_suite",
        install_requires=get_requirements(),
        python_requires="~=3.8.8"
    )