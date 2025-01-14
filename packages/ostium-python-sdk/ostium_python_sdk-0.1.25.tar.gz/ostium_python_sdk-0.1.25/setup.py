from setuptools import setup, find_packages

setup(
    name="ostium-python-sdk",
    version="0.1.25",
    packages=find_packages(),
    install_requires=[
        "web3>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.1.1",
            "pytest-cov>=3.0.0",
            "pytest-asyncio>=0.21.1",
        ],
    },
    python_requires=">=3.8",

    author="ami@ostium.io",
    description="A python based SDK developed for interacting with Ostium, a leveraged trading application for trading currencies, commodities, indices, crypto and more.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/0xOstium/ostium-python-sdk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
