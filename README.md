# FDA Adverse Event Reporting System (FAERS)
This package provides tools for working with data from the FDA Adverse Event Reporting System.

## Installation

#### 1. Install drugstandards package using PIP

`sudo pip install faers`

#### 2. Installing drugstandards from source
```
# Download this github repository and enter the following

cd faers
sudo python setup.py install
```

## Usage
To learn how to create the FDA Adverse Event Database check [here](https://github.com/mlbernauer/FAERS).

```
# Import the module
import faers

# Initialize class and establish connection to FAERS database. 
f = faers.FAERS("faers.db")

# Find events commonly reported with certain drug.
f.common_events("metoprolol")

# Compute Proportional Reporting Ratio (PRR) for a drug-event pair.
f.prr("metoprolol", "nausea")

## The prr method will standardize drug terms so that following two are equivalent
# Generic name
f.prr("metformin", "nausea")

# Brand name
f.prr("glucophage", "nausea")

# Misspellings
f.prr("glucophag", "nausea")
```
## Questions/issues/contact
mlbernauer@gmail.com
