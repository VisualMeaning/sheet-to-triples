{
    'book': '20210331 activity2project.xlsx',
    'sheet': 'activity2project',
    'lets': {
        'iri': 'vm:HE/{row[Project].as_slug}-{row[ActivityID].as_slug}',
        'parent_iri': 'vm:HE/{row[Project].as_slug}',
    },
    'non_unique': ['vm:hasInvolvement'],
    'triples': [
        ('{iri}', 'rdf:type', 'vm:ActivityInvolvement'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        # ('{iri}', 'vm:name',
        #     '{row[Project].as_slug}-{row[ActivityID].as_slug}'),
        ('{parent_iri}', 'vm:hasInvolvement',
            'vm:HE/{row[Project].as_slug}-{row[ActivityID].as_slug}'),
        ('{iri}', 'vm:relatesTo', 'vm:HE/{row[ActivityID].as_slug}'),
        ('{iri}', 'vm:activeLabel', '{row[ActiveInvolvement].as_text}'),
        ('{iri}', 'vm:passiveLabel', '{row[PassiveInvolvement].as_text}'),
        ('{iri}', 'vm:level', '{row[% Level].as_text}'),
        ('{iri}', 'vm:primary', '{row[Primary].as_text}'),
    ],
}
