{
    'data': [
        ('distributor', 'Distributor View', 'Distributors',
            'rel=stakeholder/distributor-employees'
            '+stakeholder/distributor-everyone'
            '+stakeholder/distributor-owners'),
        ('mars', 'Mars View', 'Mars Inc',
            'rel=stakeholder/mars-associates'
            '+stakeholder/mars-everyone'
            '+stakeholder/mars-leaders'),
        ('smr', 'Small Independent Retailer View', 'Small independents',
            'rel=stakeholder/small-independent-employees'
            '+stakeholder/small-independent-everyone'
            '+stakeholder/small-independent-managers'
            '+stakeholder/small-independent-owners'
            '+stakeholder/small-independent-store-staff'),
        ('human', 'Human Capital', '', 'kind=capitalTypes/human'),
        ('social', 'Social Capital', '', 'kind=capitalTypes/social'),
        ('shared', 'Shared Financial Capital', '',
            'kind=capitalTypes/sharedFinancial'),
        ('natural', 'Natural Capital', '',
            'kind=capitalTypes/environmental'),
    ],
    'lets': {
        'iri': 'vm:{row[0]}',
        'version': '20210127',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:View'),
        ('{iri}', 'vm:name', '{row[1]}'),
        ('{iri}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/mgs/{version}/overlays/'
            '{row[0]}/{{z}}-{{x}}-{{y}}.png#background:transparent'),
        ('{iri}', 'vm:useFilters', '{row[3]}'),
        ('{iri}', 'vm:asOrdinal', '{n}'),
        ('{iri}', 'vm:comment', '{row[2]}'),
        ('vm:natural', 'owl:sameAs', 'vm:environ'),
    ],
}
