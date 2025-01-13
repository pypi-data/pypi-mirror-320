from setuptools import setup, find_packages
import os

# Read the requirements file for dependencies
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
with open(requirements_path, "r") as f:
    install_requires = f.read().splitlines()

setup(
    name="graphtomation",
    version="0.2.0",
    author="Aditya Mishra",
    author_email="aditya.mishra@adimis.in",
    description="An AI utility package to build and serve Crew and LangGraph workflows as FastAPI routes, packed with reusable components for AI engineers.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/adimis-toolbox/graphtomation-server/blob/main/packages",
    packages=find_packages(include=["graphtomation", "graphtomation.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    include_package_data=True,
    keywords="AI utility Crew LangGraph FastAPI API workflows automation",
    project_urls={
        "Documentation": "https://github.com/adimis-toolbox/graphtomation-server/blob/main/packages#readme",
        "Source": "https://github.com/adimis-toolbox/graphtomation-server/blob/main/packages",
        "Issue Tracker": "https://github.com/adimis-toolbox/graphtomation-server/issues",
    },
)
