from setuptools import setup

setup(name="faers",
    install_requires = ["drugstandards"],
    version="0.1",
    description="Tools for workding with data from the FDA Adverse Event Reporting System.",
    url="http://github.com/mlbernauer/faers",
    author="Michael L. Bernauer",
    author_email="mlbernauer@gmail.com",
    license="MIT",
    packages=["faers"],
    zip_safe=False)

