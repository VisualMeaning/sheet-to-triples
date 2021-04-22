{
    'sheet': 'Pain Bright',
    'lets': {
        'iri': (
            'vm:_painpoint'
            '_{row[Stakeholder].as_slug}'
            '_{row[Painpoint / Bright spot title].as_slug}'),
        'stakeholder': 'vm:_stakeholder_{row[Stakeholder].as_slug}',
    },
    'non_unique': ['vm:name', 'vm:description'],
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Painpoint'),
        ('{iri}', 'vm:harmsCapitalType', '{row[Capital type].as_capital}'),
        ('{iri}', 'vm:name', '{row[Painpoint / Bright spot title].as_text}'),
        ('{iri}', 'vm:description',
            '{row[Painpoint / Bright spot description].as_text}'),
        ('{iri}', 'vm:ofStakeholder', '{stakeholder}'),
        ('{stakeholder}', 'rdf:type', 'vm:Stakeholder'),
        ('{iri}', 'vm:atGeoPoint', '{row[Coordinates].as_geo}'),
    ],
}
