{
    'book': 'capability2activity.xlsx',
    'sheet': 'capability',
    'allow_empty_subject': True,
    'lets': {
        'iri': 'vm:HE/{row[CapabilityID].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:HE/Capability'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:name', '{row[CapabilityID].as_text}'),
        ('{iri}', 'skos:altLabel', '{row[Abbreviation].as_text}'),
        # Present in ontology but not in sheet, seem to be using a standard
        # hasInvolvement property added by capability2activity for now
        # ('{iri}', 'vm:requiredFor', ''),
    ],
}
