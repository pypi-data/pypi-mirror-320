from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="exordiumx",
    version="0.1.0",
    author="Haveen",
    author_email="exo@exodevs.space",
    description="A custom VSCode-style logger for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ExoticCitron/exordiumx",
    packages=find_packages(include=['exordiumx', 'exordiumx.*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
)
