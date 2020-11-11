{
    'sheet': 'Person',
    'lets': {
        'iri': 'vm:HE/person-{row[Person Name].as_slug}',
    },
    'queries': {
        'Person': '''
            select ?t where {
                ?t rdfs:label 'Person' ;
            }
            ''',
    },
    'triples': [
        ('{iri}', 'rdf:type', '{Person}'),
        ('{iri}', 'vm:name', '{row[Person Name]}'),
        ('{iri}', 'vm:hasRole', 'vm:HE/role-{row[Role].as_slug}'),
        ('{iri}', 'vm:hasGroup', 'vm:HE/group-{row[Group].as_slug}'),
        ('{iri}', 'vm:hasOrg', 'vm:HE/group-{row[Organisation].as_slug}'),
        ('{iri}', 'foaf:mbox', 'mailto:{row[Email].as_text}'),
        ('{iri}', 'foaf:phone', 'tel:{row[Phone Number].as_slug}'),
        ('{iri}', 'vm:comment', '{row[VM Comment].as_text}'),
    ],
}
