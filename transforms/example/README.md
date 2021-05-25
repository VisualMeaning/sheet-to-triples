## UK Temperature Data example

This example uses [MET Office](https://www.metoffice.gov.uk/research/climate/maps-and-data/uk-and-regional-series) temperature data for the UK to create a simple set of triples containing mean, minimum and maximum temperature data for each year from 1884 through to 2020.

The transform file `uk_temp.py` contains four seperate transforms that construct the triples. See comments inside the transform file for more information on how it works.

To use, run the following command from inside the root of `sheet-to-triples`.

    python -m sheet_to_triples example/uk_temp --book "transforms/example/UK Temperature Data.xlsx"  --verbose