[
    {
        'book': '20210331 activity2activity_type.xlsx',
        'sheet': 'activity_type',
        'lets': {
            'type_iri': 'vm:HE/activitytype-{row[activity_type].as_slug}',
        },
        'triples': [
            ('{type_iri}', 'rdf:type', 'vm:HE/ActivityType'),
            ('{type_iri}', 'vm:name', '{row[activity_type].as_text}'),
            ('{type_iri}', 'vm:description', '{row[description].as_text}'),
            # in ontology but not in sheet
            # ('{type_iri}', 'vm:requires', '{capability_iri}'),
            # ('{capability_iri}', 'vm:requiredFor', '{type_iri}'),
        ],
    },
    {
        'book': '20210331 activity2activity_type.xlsx',
        'sheet': 'activity2activity_type',
        'non_unique': ['vm:hasActivity'],
        'allow_empty_subject': True,
        'lets': {
            'type_iri': 'vm:HE/activitytype-{row[activity_type].as_slug}',
            'activity_iri':  'vm:HE/{row[ActivityID].as_slug}'
        },
        'triples': [
            ('{activity_iri}', 'vm:activityType',
                'vm:HE/activitytype-{row[activity_type].as_slug}'),
            # two way relationship requested but not in ontology, so wing it
            ('{type_iri}', 'vm:hasActivity',
                'vm:HE/{row[ActivityID].as_slug}'),
        ],
    },
]
