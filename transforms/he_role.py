{
    'sheet': 'Role',
    'lets': {
        'iri': 'vm:HE/role-{row[Role Name].as_slug}',
        'level': '{row[Level]}',
    },
    'queries': {
        'Role': '''
            select ?t where {
                ?t rdfs:label 'Role' ;
            }
            ''',
    },
    'triples': [
        ('{iri}', 'rdf:type', '{Role}'),
        ('{iri}', 'vm:name', '{row[Role Name]}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
    ],
}
