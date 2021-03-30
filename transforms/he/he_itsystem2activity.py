{
    'book': '20210329 activity2itsystem.xlsx',
    'sheet': 'activity2itsystem',
    'lets': {
        'iri': 'vm:HE/{row[ITSystem].as_slug}-{row[ActivityID].as_slug}',
        'parent_iri': 'vm:HE/itsystem-{row[ITSystem].as_slug}',
        'activity_iri': 'vm:HE/{row[ActivityID].as_slug}',
    },
    'non_unique': ['vm:hasInvolvement'],
    'triples': [
        ('{iri}', 'rdf:type', 'vm:ActivityInvolvement'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:name',
            '{row[ITSystem].as_slug}-{row[ActivityID].as_slug}'),
        ('{parent_iri}', 'vm:hasInvolvement', '{iri}'),
        ('{iri}', 'vm:relatesTo', '{activity_iri}'),
        ('{iri}', 'vm:activeLabel', '{row[ActiveInvolvement].as_text}'),
        ('{iri}', 'vm:passiveLabel', '{row[PassiveInvolvement].as_text}'),
        ('{iri}', 'vm:level', '{row[% Level].as_text}'),
        ('{iri}', 'vm:primary', '{row[Primary].as_text}'),
    ],
}
