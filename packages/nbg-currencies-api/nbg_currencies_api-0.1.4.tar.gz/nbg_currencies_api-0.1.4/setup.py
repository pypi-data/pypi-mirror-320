from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="nbg-currencies-api",
    version="0.1.4",
    description="API wrapper for fetching and normalizing NBG currency rates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Illia Stebelskyi",
    author_email="illia.stebelski@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=["requests"],
    extras_require={
        "async": ["aiohttp"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Source": "https://github.com/zelnkup/nbg-currencies-api",
        "Tracker": "https://github.com/zelnkup/nbg-currencies-api/issues",
    },
)
