# use "Highways > 000 Data Ingest > 20210310 activity2project.xlsx"
{
    'sheet': 'activity2project',
    'lets': {
        'iri': 'vm:HE/{row[Project].as_slug}-{row[ActivityID].as_slug}',
        'parent_iri': 'vm:HE/orgunit-{row[Project].as_slug}',
        'activity_iri': 'vm:HE/{row[ActivityID].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:HE/ActivityInvolvement'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:name',
            '{row[Project].as_slug}-{row[ActivityID].as_slug}'),
        ('{parent_iri}', 'vm:hasInvolvement', '{iri}'),
        ('{iri}', 'vm:relatesTo', '{activity_iri}'),
        ('{iri}', 'vm:activeLabel', '{row[ActiveInvolvement].as_text}'),
        ('{iri}', 'vm:passiveLabel', '{row[PassiveInvolvement].as_text}'),
        ('{iri}', 'vm:level', '{row[% Level].as_text}'),
        ('{iri}', 'vm:primary', '{row[Primary].as_text}'),
    ],
}
