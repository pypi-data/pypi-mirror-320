import os

from setuptools import find_packages, setup

# Read the contents of README.md for long description
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="kivymd-admin",
    version="0.0.1",
    description="A command-line tool for managing KivyMD projects.",
    author="Chris Ochieng",
    author_email="mail@chrisochieng.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jangita/kivymd-admin",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "kivymd-admin = kivymd_admin.cli:main",
        ],
    },
    install_requires=[
        "kivy>=2.1.0",
        "kivymd>=1.1.1",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Natural Language :: English",
        "Environment :: Console",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.7",
)
