{
    'sheet': 'Structure',
    'lets': {
        'iri': 'vm:stakeholder/{row[Category / Stakeholder name].as_slug}',
    },
    'non_unique': ['vm:name', 'vm:description'],
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Stakeholder'),
        ('{iri}', 'vm:name', '{row[Category / Stakeholder name].as_json}@en'),
        ('{iri}', 'vm:name',
            '{row[Russian Translation: Category / Stakeholder name].as_json}'
            '@ru'),
        ('{iri}', 'vm:description', '{row[Description].as_json}@en'),
        ('{iri}', 'vm:description',
            '{row[Russian Translation: Category / Stakeholder name].as_json}'
            '@ru'),
        ('{iri}', 'vm:broader',
            'vm:stakeholder/{row[Parent Grouping].as_slug}'),
    ],
}
