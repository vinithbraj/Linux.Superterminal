#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================
 File:        setup.py
 Author:      Vinith Balakrishnan Raj
 Created:     2025-10-05
 Description: Setup configuration for SuperTerm package

 Usage:
     pip install -e .

 Notes:
     - Requires Python 3.9 or higher
     - Installs superterm as a console script

 License:
     MIT License - Copyright (c) 2025 Vinith Balakrishnan Raj
=========================================================
"""

from setuptools import setup, find_packages

setup(
    name="superterm",
    version="0.1.0",
    author="Vinith Balakrishnan Raj",
    description="An intelligent terminal powered by a local LLM via Ollama.",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "superterm=superterm.cli:app",
        ],
    },
    python_requires=">=3.9",
)
