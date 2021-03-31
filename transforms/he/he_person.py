{
    'book': '20210329 org_units.xlsx',
    'sheet': 'person',
    'lets': {
        'iri': 'vm:HE/person-{row[staff_no].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type',
            'http://xmlns.com/foaf/0.1/Person'),
        ('{iri}', 'vm:name', '{row[name].as_text}'),
        ('{iri}', 'vm:worksIn', 'vm:HE/orgunit-{row[org_unit].as_slug}'),
        # not available in current sheet
        # ('{iri}', 'vm:position', '{row[Position].as_text}'),
    ],
}
