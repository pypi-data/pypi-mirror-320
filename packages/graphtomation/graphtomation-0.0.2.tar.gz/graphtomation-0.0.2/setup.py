from setuptools import setup, find_packages
import os

requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
with open(requirements_path, "r") as f:
    install_requires = f.read().splitlines()

setup(
    name="graphtomation",
    version="0.0.2",
    author="Aditya Mishra",
    author_email="aditya.mishra@adimis.in",
    description="A FastAPI utility for exposing CrewAI functionalities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dev-adimis/graphtomation",
    packages=find_packages(include=["graphtomation", "graphtomation.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    include_package_data=True,
)
