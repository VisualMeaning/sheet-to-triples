[
    # First define our country object that we will attach temperature
    # measurements to - the source workbook has data for just the UK.
    {
        'data': [
            ('UK', 'United Kingdom')
        ],
        'lets': {
            'country_iri': 'vm:temperature-{row[0]}',
        },
        'triples': [
            ('{country_iri}', 'rdf:type', 'vm:Country'),
            ('{country_iri}', 'vm:name', '{row[1]}'),
        ],
    },
    # Get annual mean temp measurements for the UK from the relevant sheet
    # in the workbook. As this is our first set of temperature data
    # we'll also define a TemperatureYear object that can have
    # max, min and mean temperature attributes. We'll also attach
    # this TemperatureMeasurement to the UK object we created in the
    # previous transform via hasTemperatureMeasurement.
    {
        'book': 'UK Temperature Data.xlsx',
        'sheet': 'Mean temp',
        'lets': {
            'year_iri': 'vm:temperature-UK-{row[year].as_slug}',
            'uk_iri': 'vm:temperature-UK'
        },
        'non_unique': ['vm:hasTemperatureMeasurement'],
        'triples': [
            ('{year_iri}', 'rdf:type', 'vm:temperatureMeasurement'),
            ('{year_iri}', 'vm:name', 'UK - {row[year].as_text}'),
            ('{year_iri}', 'vm:meanTemp', '{row[ann].as_text}'),
            ('{uk_iri}', 'vm:hasTemperatureMeasurement', '{year_iri}'),
        ],
    },
    # Get annual max temp measurements for the UK. We've already defined our
    # TemperatureYear in the mean temp transform, so no need to do it again
    # - we just create a new maxTemp property for it from the Max Temp sheet.
    {
        'book': 'UK Temperature Data.xlsx',
        'sheet': 'Max temp',
        'lets': {
            'year_iri': 'vm:temperature-UK-{row[year].as_slug}',
        },
        'triples': [
            ('{year_iri}', 'vm:maxTemp', '{row[ann].as_text}'),
        ],
    },
    # Get annual min temp measurements for the UK. Like maxTemp, this involves
    # creating a single minTemp property for each TemperatureYear.
    {
        'book': 'UK Temperature Data.xlsx',
        'sheet': 'Min temp',
        'lets': {
            'year_iri': 'vm:temperature-UK-{row[year].as_slug}',
        },
        'triples': [
            ('{year_iri}', 'vm:minTemp', '{row[ann].as_text}'),
        ],
    }
]
