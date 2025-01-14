version = "1.0.5"

from setuptools import setup, find_packages

with open("pyproject.toml", "r") as f:
    lines = f.readlines()
    for idx, line in enumerate(lines):
        print(idx)
        if "version" in line:
            with open("pyproject.toml", "w") as ff:
                lines[idx] = f'version = "{version}"\n'
                ff.write("".join(lines))

            break

setup(
    name="oracle.luau",
    version=version,
    description="An API wrapper for the Oracle Luau decompiler.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ActualMasterOogway",
    author_email="realmasteroogway.contact@gmail.com",
    url="https://github.com/ActualMasterOogway/oracle.luau",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    license="GPL-3.0",
    keywords = [
        "roblox", 
        "lua", 
        "luau",
        "decompiler",
        "bytecode",
        "deserializer",
        "compile"
    ],
    project_urls={
       "Documentation": "https://your-documentation-url.com",
       "GitHub": "https://github.com/ActualMasterOogway/oracle.luau",
       "Bug Tracker": "https://github.com/ActualMasterOogway/oracle.luau/issues",
    },
    python_requires=">=3.6",
    install_requires=[
        "aiohttp>=3.8.1"
    ],
)
