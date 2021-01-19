{
    'data': [
        ('distributor', 'Distributor View',
            'rel=stakeholder/distributor-employees'
            '+stakeholder/distributor-everyone'
            '+stakeholder/distributor-owners'),
        ('mars', 'Mars View', 'rel=stakeholder/mars-associates'
            '+stakeholder/mars-everyone'
            '+stakeholder/mars-leaders'),
        ('smr', 'Small Independent Retailer View',
            'rel=stakeholder/small-independent-employees'
            '+stakeholder/small-independent-everyone'
            '+stakeholder/small-independent-managers'
            '+stakeholder/small-independent-owners'
            '+stakeholder/small-independent-store-staff'),
        ('human', 'Human Capital', 'kind=capitalTypes/human'),
        ('social', 'Social Capital', 'kind=capitalTypes/social'),
        ('shared', 'Shared Financial Capital',
            'kind=capitalTypes/sharedFinancial'),
        ('environ', 'Natural Capital', 'kind=capitalTypes/environmental'),
    ],
    'lets': {
        'iri': 'vm:{row[0]}',
        'version': '20210118',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:View'),
        ('{iri}', 'vm:name', '{row[1]}'),
        ('{iri}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/mgs/{version}/overlays/'
            '{row[0]}/{{z}}-{{x}}-{{y}}.png#background:transparent'),
        ('{iri}', 'vm:useFilters', '{row[2]}'),
        ('{iri}', 'vm:asOrdinal', '{n}'),
    ],
}
