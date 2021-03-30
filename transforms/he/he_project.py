# no guidelines for how to treat this in ontology so just wing it
{
    'book': '20210311 activity2project.xlsx',
    'sheet': 'project',
    'lets': {
        'iri': 'vm:HE/{row[project].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Project'),
        ('{iri}', 'vm:description', '{row[description].as_text}'),
        ('{iri}', 'vm:name', '{row[project].as_text}'),
        # staffNumber has vanished from the sheet
        # ('{iri}', 'vm:hasOwner', 'vm:HE/person-{row[StaffNumber].as_slug}'),
        ('{iri}', 'vm:hasType', '{row[Type].as_text}'),
        ('{iri}', 'vm:hasStatus', '{row[Status].as_text}'),
    ],
}
