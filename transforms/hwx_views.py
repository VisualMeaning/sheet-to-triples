{
    'data': [
        ('activity', 'activity', '', 'Activity View', 'a=HE/Activity'),
        ('org', 'org', 'org', 'Organisation View',
            'a=org:OrganisationalUnit'),
        ('orgpeople', 'org', 'org', 'Organisation + People View',
            'a=org:OrganisationalUnit+foaf:Person'),
    ],
    'lets': {
        'iri': 'vm:{row[0]}',
        'version': '20210310',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:View'),
        ('{iri}', 'vm:name', '{row[3]}'),
        ('{iri}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/hwx/{version}/overlays/'
            '{row[2].as_text}/{{z}}-{{x}}-{{y}}.png#background:#fff'),
        ('{iri}', 'vm:useFilters', '{row[4]}'),
        ('{iri}', 'vm:asOrdinal', '{n}'),
        ('{iri}', 'vm:comment', '{row[1]}'),
    ],
}
