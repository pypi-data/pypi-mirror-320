from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sherlock-scanner",
    version="1.0.1",
    description="A Python security scanner for hardcoded secrets and API keys.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Omeriko",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=["click"],
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
