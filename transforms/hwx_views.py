{
    'data': [
        ('activity', 'activity', '', 'Activity View',
            'plottable=t&group=type'),
        ('org', 'org', 'org', 'Organisation View',
            'a=org:OrganisationalUnit'),
        ('orgpeople', 'org', 'org', 'Organisation + People View',
            'a=org:OrganisationalUnit+foaf:Person&group=org'),
        ('cap', 'cap', 'cap', 'Capability View', 'a=HE/Capability'),
    ],
    'lets': {
        'iri': 'vm:{row[0]}',
        'version': '20210311',
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
