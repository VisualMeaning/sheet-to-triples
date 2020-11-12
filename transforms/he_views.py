{
    'data': [
        ('process', 'Process'),
        ('org-structure', 'Org Structure'),
    ],
    'lets': {
        'iri': 'vm:view-he-{row[0]}',
        'version': '20201111',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:View'),
        ('{iri}', 'vm:name', '{row[1]}'),
        ('{iri}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/hwtest/{version}/overlays/'
             '{row[0]}/{{z}}-{{x}}-{{y}}.png#background:transparent'),
        ('{iri}', 'vm:asOrdinal', '{n}'),
    ],
}
