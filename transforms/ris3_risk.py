[{
    'sheet': 'Risk Map Definitions',
    'lets': {
        'iri': 'vm:HE/_{row[Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:HE/{row[Class / Category].as_uc}'),
        ('{iri}', 'vm:name', '{row[Name].as_text}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'owl:sameAs', 'vm:HE/_{row[Map Label Differs?].as_slug}'),
    ],
}, {
    'sheet': 'Risk Map Relationships',
    'lets': {},
    'non_unique': ['vm:HE/causes', 'vm:HE/stronglycauses'],
    'triples': [
        (
            'vm:HE/_{row[Subject].as_slug}',
            'vm:HE/{row[Predicate].as_text}',
            'vm:HE/_{row[Object].as_slug}',
        ),
    ],
}]
