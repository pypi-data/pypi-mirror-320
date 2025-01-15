from setuptools import setup, find_packages
import pytest

# Fonction pour exécuter les tests
def run_tests():
    pytest.main()


setup(
    name="system-report",
    version="1.0.0",
    author="John Doe",
    author_email="john.doe@admsys.com",
    description="A Python package to generate and save system reports.",
    long_description=open("system_report/README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "psutil"
    ],
    entry_points={
        "console_scripts": [
            "system-report=system_report:main"
        ]
    },
    include_package_data=True,
    test_suite='__main__.run_tests',
)
