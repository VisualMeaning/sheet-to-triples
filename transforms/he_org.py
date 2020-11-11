{
    'sheet': 'Organisation',
    'lets': {
        'iri': 'vm:HE/group-{row[Organisation Name].as_slug}',
        'class_name': '{row[Class].as_text}',
    },
    'queries': {
        'class': '''
            select ?t where {
                ?t rdfs:label ?class_name ;
            }
            ''',
    },
    'triples': [
        ('{iri}', 'rdf:type', '{class}'),
        ('{iri}', 'vm:name', '{row[Organisation Name]}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
    ],
}
