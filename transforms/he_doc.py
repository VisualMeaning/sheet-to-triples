{
    'sheet': 'Document',
    'lets': {
        'iri': 'vm:HE/document-{row[Document Name].as_slug}',
    },
    'queries': {
        'Document': '''
            select ?t where {
                ?t rdfs:label 'Document' ;
            }
            ''',
    },
    'triples': [
        ('{iri}', 'rdf:type', '{Document}'),
        ('{iri}', 'vm:name', '{row[Document Name]}'),
        ('{iri}', 'skos:altLabel', '{row[altLabel].as_text}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:hasDocumentStatus', '{row[VM Status].as_text}'),
        ('{iri}', 'vm:hasImportance', '{row[VM Importance].as_text}'),
        ('{iri}', 'vm:atUrl', '{row[File]}'),
        ('{iri}', 'vm:HE/ownedByGroup',
            'vm:HE/group-{row[Owned by (Group)].as_slug}'),
        ('{iri}', 'vm:HE/relatesToGroup',
            'vm:HE/group-{row[Relates to (Group)].as_slug}'),
        ('{iri}', 'vm:HE/receivedFrom',
            'vm:HE/person-{row[Received from (Person)].as_slug}'),
        ('{iri}', 'vm:comment', '{row[VM Comment].as_text}'),
    ],
}
