{
    'sheet': 'Brazil Pain Bright',
    'lets': {
        'iri': '{row[Bright/Pain].as_type_prefix}{row[Unique Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', '{row[Bright/Pain].as_type}'),
        ('{iri}', 'vm:name', '{row[Painpoint / Bright spot title]}'),
        ('{iri}', 'vm:description',
            '{row[Painpoint / Bright spot description]}'),
        ('{iri}', '{row[Bright/Pain].as_capital_effect}',
            '{row[Category / Capital].as_capital}'),
        ('{iri}', 'vm:ofStakeholder',
            'vm:stakeholder/{row[Stakeholder].as_slug}'),
        ('{iri}', 'vm:relates',
            'vm:stakeholder/{row[In relation to:].as_slug}'),
        ('{iri}', 'vm:atGeoPoint', '{row[Coordinates].as_geo}'),
        ('{iri}', 'owl:sameAs', 'vm:painpoint/{row[Unique Name].as_slug}'),
    ],
}
