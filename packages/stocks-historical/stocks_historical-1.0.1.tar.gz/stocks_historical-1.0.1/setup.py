from setuptools import setup, find_packages

setup(
    name="stocks_historical",
    version="1.0.1",
    author="Daniel Mantey",
    author_email="contactmantey@gmail.com",
    description="A Python package to access historical stock data for NASDAQ and NYSE.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mantey-github/stocks-historical",
    download_url="https://github.com/mantey-github/stocks-historical/releases",
    packages=find_packages(),
    install_requires=["requests", "pandas", "setuptools"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
