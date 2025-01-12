from setuptools import setup, find_packages

setup(
    name="sherlock-scanner",
    version="1.0.0",
    description="Sherlock: A simple Python-based security scanner for hardcoded secrets and API keys.",
    author="Omer Revach",
    author_email="idonttellyou@example.com",
    packages=find_packages(),
    install_requires=[
        "click"
    ],
    entry_points={
        "console_scripts": [
            "sherlock=sherlock.cli:run_scan"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
