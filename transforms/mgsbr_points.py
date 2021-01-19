{
    'sheet': 'Brazil Pain Bright',
    'lets': {
        'iri': 'vm:painpoint/{row[Unique Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Painpoint'),
        ('{iri}', 'vm:name', '{row[Painpoint / Bright spot title]}'),
        ('{iri}', 'vm:description',
            '{row[Painpoint / Bright spot description]}'),
        ('{iri}', 'vm:harmsCapitalType',
            '{row[Category / Capital].as_capital}'),
        ('{iri}', 'vm:ofStakeholder',
            'vm:stakeholder/{row[Stakeholder].as_slug}'),
        ('{iri}', 'vm:relates',
            'vm:stakeholder/{row[In relation to:].as_slug}'),
        ('{iri}', 'vm:atGeoPoint', '{row[Coordinates].as_geo}'),
        ('{iri}', 'vm:actuallyBright', '{row[Bright/Pain].as_text}'),
    ],
}
