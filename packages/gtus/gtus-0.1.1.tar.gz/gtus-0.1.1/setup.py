from setuptools import setup, find_packages

setup(
    name="gtus",
    version="0.1.1",
    description="A Python package to collect and analyze Google Trends data for US states.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Levent Bulut",
    author_email="levent.bulut@unt.edu",
    license="MIT",
    url="https://github.com/leventbulut/gtus",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pandas>=1.3.0",
        "pytrends>=4.8.0",
        "aiohttp>=3.8.0",
        "openpyxl>=3.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
