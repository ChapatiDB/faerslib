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

#### Setup
```
# Import the module
import faers

# Initialize class and establish connection to FAERS database.
# This will create an object containing records from the UNITED STATES
# for all available years. Due to the size of the database this could take some
# time. 
f = faers.FAERS("faers.db")

# Create object using records from Japan and year 2012.
f = faers.FAERS("faers.db", countries="japan", years=2012)

# Create objects using records from United States, Japan and years 2010, 2011, 2012.
f = faers.FAERS("faers.db", countries=["japan", "united states"], years = [2010, 2011, 2012])
```

#### Utility functions
```
# Find associated events by drug.  Returns a list sorted by frequency.
f.associated_events("metoprolol")

# Find associated drugs by event.  Returns a list sorted by frequency.
f.associated_drugs("progressive multifocal leukoencephalopathy")

# Find drug counts.  Returns a list of drug names sorted by frequency.
f.drug_counts()

# Find event counts.  Returns a list of events sorted by frequency.
f.event_counts()

# Find events containing a phrase.  Returns a list of events containing the phrase.
f.find_like_events("fatigue")

# Find drug names by matching phrase.  Returns a list of drug names
# who's names match a given pattern/phrase.
f.find_like_drugs("pril")
```

#### Data Mining Algorithms
##### Proportional Reporting Ratio
```
# Compute Proportional Reporting Ratio (PRR) for a drug-event pair.
# Returns the PRR as well as 95% CI
f.prr("metoprolol", "nausea")

## The prr method will standardize drug terms so that following two are equivalent
# Generic name
f.prr("metformin", "nausea")

# Brand name
f.prr("glucophage", "nausea")

# Misspellings
f.prr("glucophag", "nausea")

# Compute PRR for all events given a drug name.
f.mine_prr_by_drug("natalizumab")

# Compute PRR for all drugs given an event.
f.mine_prr_by_event("progressive multifocal leukoencephalopathy")
```
##### Reporting Odds Ratio (ROR)
```
# Compute the Reporting Odds Ratio (ROR) for a given drug-event pair.
# Returns the ROR as well as 95% CI.
f.ror("natalizumab", "progressive multifocal leukoencephalopathy")
```

##### Multi-item Gamma Poisson Shrinker (MGPS)
```
# Compute the Multi-item Gamma Poisson Shrinker (MGPS) for a given drug-event pair.
f.mgps("natalizumab", "progressive multifocal leukoencephalopathy")
```

## Questions/issues/contact
mlbernauer@gmail.com
