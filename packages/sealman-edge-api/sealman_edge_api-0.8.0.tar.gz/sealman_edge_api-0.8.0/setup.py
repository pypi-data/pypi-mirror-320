import os
import json
import shutil
from setuptools import setup, find_packages


with open(os.path.join(os.getcwd(), "sealman_edge_api", "version.json"), "r") as file:
    version = json.loads(file.read()).get("version")
    main, feature, build = version.split(".")
    version = ".".join([main, feature, build])

print(f"build version: {version} ?")

for _dir in ["sealman_edge_api.egg-info", "build", "dist"]:
    try:
        shutil.rmtree(_dir)
    except:
        pass

with open(os.path.join(os.getcwd(), "version.json"), "w") as file:
    file.write(json.dumps({"version": version}))


setup(
    name='sealman-edge-api',
    version=version,
    packages=find_packages(),
    author="Thomas Baur",
    author_email="thomas.baur@gea.com",
    description="SEALMAN Edge lib for easy communication within the SEALMAN Open Source Ecosystem",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Wolf-Pack-Foundation/sealman-lib-edge-api",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=[
        "paho-mqtt == 1.6.1",
        "jsonschema >= 4.21.1"
    ],
    package_data={
        'sealman_edge_api': ['schemas/*.json', "version.json"]
    },
    include_package_data=True,
)
