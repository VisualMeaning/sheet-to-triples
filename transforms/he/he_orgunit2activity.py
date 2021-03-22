# use "Highways > 000 Data Ingest > 20210305 orgunit2actvity - master.xlsx"
{
    'sheet': 'org_unit2activity',
    'lets': {
        'iri': ('vm:HE/orgunit-{row[OrgUnitID].as_slug}'
                '-{row[ActivityID].as_slug}'),
        'parent_iri': 'vm:HE/orgunit-{row[OrgUnitID].as_slug}',
        'activity_iri': 'vm:HE/{row[ActivityID].as_slug}',
    },
    'allow_empty_subject': True,
    'skip_empty_rows': True,
    'non_unique': ['vm:hasInvolvement'],
    'triples': [
        ('{iri}', 'rdf:type', 'vm:HE/ActivityInvolvement'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        # name is just here so that I can see it in the explorer view for now
        ('{iri}', 'vm:name',
            'orgunit-{row[OrgUnitID].as_slug}-{row[ActivityID].as_slug}'),
        ('{parent_iri}', 'vm:hasInvolvement', '{iri}'),
        ('{iri}', 'vm:relatesTo', '{activity_iri}'),
        ('{iri}', 'vm:activeLabel',
            '{row[ActiveInvolvement].as_text}'),
        ('{iri}', 'vm:passiveLabel',
            '{row[PassiveInvolvement].as_text}'),
        ('{iri}', 'vm:level', '{row[% Level].as_text}'),
        ('{iri}', 'vm:primary', '{row[Primary].as_text}'),
    ],
}
