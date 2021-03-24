# uses 000 Data Ingest > 20210308 activity2activity_type.xlsx
{
    'sheet': 'activity2activity_type',
    'non_unique': ['vm:hasActivity'],
    'allow_empty_subject': True,
    'lets': {
        'type_iri': 'vm:HE/activitytype-{row[activity_type].as_slug}',
        'activity_iri':  'vm:HE/{row[ActivityID].as_slug}'
    },
    'triples': [
        ('{type_iri}', 'rdf:type', 'vm:HE/ActivityType'),
        ('{type_iri}', 'vm:name', '{row[activity_type].as_text}'),
        ('{activity_iri}', 'vm:activityType', '{type_iri}'),
        # two way relationship requested but not in ontology, so wing it
        ('{type_iri}', 'vm:hasActivity', '{activity_iri}'),
        # in ontology but not in sheet
        # ('{type_iri}', 'vm:requires', '{capability_iri}'),
        # ('{capability_iri}', 'vm:requiredFor', '{type_iri}'),
    ],
}
