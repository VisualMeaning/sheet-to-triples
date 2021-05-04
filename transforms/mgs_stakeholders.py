{
    'sheet': 'Stakeholder structure',
    'lets': {
        'iri': 'vm:_stakeholder_{row[Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Stakeholder'),
        ('{iri}', 'vm:name', '{row[Name]}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:broader',
            'vm:_stakeholder_{row[Parent Grouping].as_slug}'),
        ('{iri}', 'vm:link', '{row[Link to Stakeholder Portrait].as_text}'),
        ('{iri}', 'owl:sameAs',
            'vm:_stakeholder_{row[Label on Map (if different)].as_slug}'),

    ],
}
