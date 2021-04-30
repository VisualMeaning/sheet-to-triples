{
    'data': [
        ('distributor', 'Distributor View', 'Distributors',
            'rel=_stakeholder_distributor-employees'
            '+_stakeholder_distributor-everyone'
            '+_stakeholder_distributor-owners'),
        ('mars', 'Mars View', 'Mars Inc',
            'rel=_stakeholder_mars-associates'
            '+_stakeholder_mars-everyone'
            '+_stakeholder_mars-leaders'),
        ('smr', 'Small Independent Retailer View', 'Small independents',
            'rel=_stakeholder_small-independent-employees'
            '+_stakeholder_small-independent-everyone'
            '+_stakeholder_small-independent-managers'
            '+_stakeholder_small-independent-owners'
            '+_stakeholder_small-independent-store-staff'),
        ('human', 'Human Capital', '', 'kind=capitalTypes/human'),
        ('social', 'Social Capital', '', 'kind=capitalTypes/social'),
        ('shared', 'Shared Financial Capital', '',
            'kind=capitalTypes/sharedFinancial'),
        ('natural', 'Natural Capital', '',
            'kind=capitalTypes/environmental'),
    ],
    'lets': {
        'iri': 'vm:{row[0]}',
        'version': '20210429',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:View'),
        ('{iri}', 'vm:name', '{row[1]}'),
        ('{iri}', 'vm:useFilters', '{row[3]}'),
        ('{iri}', 'vm:asOrdinal', '{n}'),
        ('{iri}', 'vm:comment', '{row[2]}'),
    ],
}
