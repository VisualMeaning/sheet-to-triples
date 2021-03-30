{
    'book': 'capability2activity.xlsx',
    'sheet': 'cap2activity',
    'lets': {
        'iri': 'vm:HE/{row[CapabilityID].as_slug}-{row[ActivityID].as_slug}',
        'activity_iri': 'vm:HE/{row[ActivityID].as_slug}',
    },
    'allow_empty_subject': True,
    'non_unique': ['vm:hasInvolvement'],
    'triples': [
        ('{iri}', 'rdf:type', 'vm:ActivityInvolvement'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:name',
            '{row[CapabilityID].as_slug}-{row[ActivityID].as_slug}'),
        ('vm:HE/{row[CapabilityID].as_slug}', 'vm:hasInvolvement', '{iri}'),
        ('{iri}', 'vm:relatesTo', '{activity_iri}'),
        ('{iri}', 'vm:activeLabel', '{row[ActiveInvolvement].as_text}'),
        ('{iri}', 'vm:passiveLabel', '{row[PassiveInvolvement].as_text}'),
        ('{iri}', 'vm:level', '{row[% Level].as_text}'),
        ('{iri}', 'vm:primary', '{row[Primary].as_text}'),
    ],
}
