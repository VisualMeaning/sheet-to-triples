{
    'sheet': 'Group',
    'lets': {
        'iri': 'vm:HE/group-{row[Group Name].as_slug}',
        'class_iri': 'vm:HE/{row[Sub-Class].as_uc}',
    },
    'triples': [
        ('{class_iri}', 'rdf:type', 'rdfs:Class'),
        ('{class_iri}', 'rdfs:subClassOf', 'vm:HE/Group'),
        ('vm:HE/Group', 'rdf:type', 'rdfs:Class'),
        ('vm:HE/Group', 'rdfs:label', 'Group'),
        ('{class_iri}', 'rdfs:label', '{row[Sub-Class]}'),
        ('{iri}', 'rdf:type', '{class_iri}'),
        ('{iri}', 'vm:name', '{row[Group Name]}'),
        ('{iri}', 'skos:altLabel', '{row[altLabel].as_text}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:HE/leadBy',
            'vm:HE/person-{row[Lead by (person)].as_slug}'),
        ('{iri}', 'vm:HE/isSubgroupOf',
            'vm:HE/group-{row[Sub-group of].as_slug}'),
        ('{iri}', 'vm:comment', '{row[VM Comment].as_text}'),
    ],
}
