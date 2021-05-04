{
    'book': 'MGS DS Russia input sheet v4.xlsx',
    'sheet': 'Painpoints',
    'lets': {
        'iri': (
            '{row[Bright/Pain].as_type_prefix}'
            '{row[Painpoint / Bright spot title].as_slug}'),
    },
    'triples': [
        ('{iri}', 'rdf:type', '{row[Bright/Pain].as_type}'),
        ('{iri}', 'vm:name', '{row[Painpoint / Bright spot title]}'),
        ('{iri}', 'vm:description',
            '{row[Painpoint / Bright spot description]}'),
        ('{iri}', '{row[Bright/Pain].as_capital_effect}',
            '{row[Category / Capital].as_capital}'),
        ('{iri}', 'vm:ofStakeholder',
            'vm:_stakeholder_{row[Stakeholder].as_slug}'),
        ('{iri}', 'vm:relates',
         'vm:_stakeholder_{row[In relation to:].as_slug}'),
        ('{iri}', 'vm:atGeoPoint', '{row[Coordinates].as_geo}'),
        ('{iri}', 'vm:region', 'vm:_Russia'),
    ],
}
