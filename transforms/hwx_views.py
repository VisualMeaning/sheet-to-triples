{
    'data': [
        ('HE/org', 'org', 'Organisation View', 'org', ''),
    ],
    'lets': {
        'iri': 'vm:{row[0]}',
        'version': '20210308',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:View'),
        ('{iri}', 'vm:name', '{row[2]}'),
        ('{iri}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/hwx/{version}/overlays/'
            '{row[1]}/{{z}}-{{x}}-{{y}}.png#background:#fff'),
        ('{iri}', 'vm:useFilters', '{row[4]}'),
        ('{iri}', 'vm:asOrdinal', '{n}'),
        ('{iri}', 'vm:comment', '{row[3]}'),
    ],
}
