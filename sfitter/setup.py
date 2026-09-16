from setuptools import setup, find_packages

HTTPS_GITHUB_URL = "https://github.com/heidelberg-hepml/sfitter"

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = ["numpy", "pandas", "scipy", "tables", "torch", "matplotlib", "tqdm"]

setup(
    name="sfitter",
    version="0.8.15",
    author="Theo Heimel, Nikita Schmal",
    author_email="heimel@thphys.uni-heidelberg.de",
    description="Painless fitting tool",
    long_description=long_description,
    long_description_content_type="text/md",
    url=HTTPS_GITHUB_URL,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements,
    entry_points={"console_scripts": ["sfitter=sfitter.__main__:main"]},
)
