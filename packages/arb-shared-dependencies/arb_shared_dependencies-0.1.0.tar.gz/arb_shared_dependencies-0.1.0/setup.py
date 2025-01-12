from setuptools import setup, find_packages

setup(
    name="arb-shared-dependencies",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "web3>=6.3.0",
        "python-dotenv>=1.0.0"
    ],
    author="justmert",
    author_email="",  # Add your email if you want
    description="Shared utilities for Arbitrum development",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    url="https://github.com/justmert/arb-shared-dependencies",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
