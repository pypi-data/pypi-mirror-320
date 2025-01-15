"""Setup configuration for Tamga package."""
from setuptools import setup, find_packages

# Read the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tamga",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["pytz>=2024.1"],
    
    # Metadata
    author="Dogukan Urker",
    author_email="dogukanurker@icloud.com",
    description="A beautiful and customizable logger for Python web applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dogukanurker/tamga",
    project_urls={
        "Bug Tracker": "https://github.com/dogukanurker/tamga/issues",
        "Documentation": "https://github.com/dogukanurker/tamga#readme",
        "Source Code": "https://github.com/dogukanurker/tamga",
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Framework :: FastAPI",
    ],
    
    # Package config
    python_requires=">=3.10",
    keywords="logging logger colorful web flask fastapi",
    include_package_data=True,
    zip_safe=False,
) 