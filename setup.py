#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EGX Pro Terminal v26 - Setup Configuration
نظام تحليلي احترافي للبورصة المصرية
"""

from setuptools import setup, find_packages
import os

# قراءة ملف README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# قراءة ملف requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="egx-pro-terminal",
    version="26.0.0",
    author="m02417710-maker",
    author_email="support@egxpro.com",
    description="نظام تحليلي احترافي للبورصة المصرية مع ميزات متقدمة",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m02417710-maker/m02417710_",
    project_urls={
        "Bug Tracker": "https://github.com/m02417710-maker/m02417710_/issues",
        "Documentation": "https://github.com/m02417710-maker/m02417710_/wiki",
        "Source Code": "https://github.com/m02417710-maker/m02417710_",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Streamlit",
        "Natural Language :: Arabic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
            "pylint>=2.12",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "egx-pro-terminal=egx_pro_terminal.cli:main",
        ],
    },
    keywords=[
        "egx",
        "egyptian",
        "stock",
        "market",
        "trading",
        "analysis",
        "terminal",
        "alerts",
        "risk",
        "portfolio",
        "strategies",
        "البورصة المصرية",
        "تحليل أسهم",
        "نظام تداول",
    ],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
)
