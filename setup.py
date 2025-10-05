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
