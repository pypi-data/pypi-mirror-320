"""Setup configuration for quickly package."""

import os
import re

from setuptools import find_packages, setup

# Read the contents of README file
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    readme = f.read()

# Read version from version.py using regex pattern
with open(os.path.join("quickly", "version.py"), encoding="utf-8") as f:
    content = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="quickly-plot",
    version=version,
    description="A fluent interface for matplotlib plotting",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Alexander Procelewski",
    author_email="alexprocelewski@gmail.com",
    url="https://github.com/alexthe2/quickly",
    
    packages=find_packages(),
    package_dir={'quickly': 'quickly'},
    
    install_requires=[
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "pandas>=1.2.0",
        "numpy>=1.19.0",
        "scipy>=1.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "isort>=5.9.0",
            "flake8>=3.9.0",
            "mypy>=0.900",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.7",
    project_urls={
        "Bug Reports": "https://github.com/alexthe2/quickly/issues",
        "Source": "https://github.com/alexthe2/quickly",
        "Documentation": "https://quickly.readthedocs.io/",
    },
    keywords=[
        "matplotlib",
        "plotting",
        "data visualization",
        "builder pattern",
        "fluent interface",
    ],
)