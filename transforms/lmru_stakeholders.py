{
    'sheet': 'Structure',
    'lets': {
        'iri': 'vm:_stakeholder_{row[Category / Stakeholder name].as_slug}',
    },
    'non_unique': ['vm:comment', 'vm:name', 'vm:description'],
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
            'vm:_stakeholder_{row[Parent Grouping].as_slug}'),
        ('{iri}', 'vm:comment', '{row[Map label name].as_json}@en'),
        ('{iri}', 'vm:comment',
            '{row[Russian translation: label name].as_json}@ru'),
    ],
}
