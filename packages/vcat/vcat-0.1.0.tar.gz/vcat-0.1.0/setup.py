from setuptools import setup, find_packages

setup(
    name="vcat",
    version="0.1.0",
    description="A CLI tool to generates human friendly visualizations for files.",
    author="Alex Xi",
    url="https://github.com/alexxi19/vcat",  # Replace with your GitHub repo
    packages=find_packages(),
    install_requires=[
        "openai",  # Required dependency
    ],
    entry_points={
        "console_scripts": [
            "vcat=vcat.cli:main",  # Links `vcat` command to `main()` in `cli.py`
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Adjust based on your requirements
)
