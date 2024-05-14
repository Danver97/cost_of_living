# Cost of Living

This repo provides a qualitative analysis of costs of living in several EU and non-EU cities.  
All data has been sourced from Numbeo.com around May 2024.

## Installation requirements
Make sure to have python 3 installed. Then run:
```sh
git clone https://github.com/Danver97/cost_of_living.git
cd cost_of_living
pip install -r requirements.txt
```

## Usage

This projects has been designed to be open for modification.

Currently there are two scripts:
- `main.py` used for gathering data. It writes (overwrites if already present) `cities.csv`.
- `analysis.py` used for plotting and analysis. It reads `cities.csv` in the same repo directory.

A small dataset of ~100 cities is already provided under `cities.csv`. Feel free to add more countries and cities to collect in `main.py`.
