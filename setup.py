from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gmail-archivist",
    version="0.1.0",
    author="Andrew Guo",
    author_email="",
    description="A Python tool to automatically archive old Gmail messages while preserving starred conversations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrewguo5/gmail-archivist",
    py_modules=["archive_messages"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gmail-archivist=archive_messages:main",
        ],
    },
)
