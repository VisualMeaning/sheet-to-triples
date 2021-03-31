{
    'book': '20210331 org_unit2activity - master.xlsx',
    'sheet': 'org_unit2activity',
    'lets': {
        'iri': ('vm:HE/orgunit-{row[OrgUnitID].as_slug}'
                '-{row[ActivityID].as_slug}'),
        'parent_iri': 'vm:HE/orgunit-{row[OrgUnitID].as_slug}',
    },
    'allow_empty_subject': True,
    'skip_empty_rows': True,
    'non_unique': ['vm:hasInvolvement'],
    'triples': [
        ('{iri}', 'rdf:type', 'vm:ActivityInvolvement'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        # name is just here so that I can see it in the explorer view for now
        # ('{iri}', 'vm:name',
        #     'orgunit-{row[OrgUnitID].as_slug}-{row[ActivityID].as_slug}'),
        ('{parent_iri}', 'vm:hasInvolvement',
            ('vm:HE/orgunit-{row[OrgUnitID].as_slug}'
             '-{row[ActivityID].as_slug}')),
        ('{iri}', 'vm:relatesTo', 'vm:HE/{row[ActivityID].as_slug}'),
        ('{iri}', 'vm:activeLabel',
            '{row[ActiveInvolvement].as_text}'),
        ('{iri}', 'vm:passiveLabel',
            '{row[PassiveInvolvement].as_text}'),
        ('{iri}', 'vm:level', '{row[% Level].as_text}'),
        ('{iri}', 'vm:primary', '{row[Primary].as_text}'),
    ],
}
