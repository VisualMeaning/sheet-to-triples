{
    'sheet': 'Brazil Ontology',
    'lets': {
        'iri': 'vm:stakeholder/{row[Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Stakeholder'),
        ('{iri}', 'vm:name', '{row[Name]}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:broader', 'vm:stakeholder/{row[Parent Grouping].as_slug}'),
    ],
}

