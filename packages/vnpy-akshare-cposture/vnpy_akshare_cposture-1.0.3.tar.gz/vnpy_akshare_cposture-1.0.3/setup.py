from setuptools import setup, find_packages

setup(
    name="vnpy-akshare-cposture",
    version="1.0.3",
    author="cposture",
    author_email="cposture@126.com",
    license="MIT",
    url="https://github.com/cposture/vnpy_akshare",
    description="AKShare datafeed for VeighNa quant trading framework",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=["vnpy_akshare"],
    package_dir={"vnpy_akshare": "vnpy_akshare"},
    install_requires=[
        "vnpy>=3.0.0",
        "akshare>=1.0.0"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7"
)
