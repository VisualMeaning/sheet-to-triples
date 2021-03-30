# use "Highways > 000 Ontology > highways_SMP_ingest.xlsx" -
# this really just needs an additional column in the big sheet or
# the orgunit2activity sheets
{
    'book': '20210329 org_unit2activity - master.xlsx',
    'sheet': 'org_unit',
    'lets': {
        'iri': 'vm:HE/orgunit-{row[leader_staff_number].as_slug}',
        'parent_iri': 'vm:HE/orgunit-{row[parent_org_staff_number].as_slug}',
    },
    'allow_empty_subject': True,
    'triples': [
        ('{iri}', 'rdf:type',
            'http://www.w3.org/ns/org#OrganisationalUnit'),
        ('{iri}', 'vm:name', '{row[merged_name].as_text}'),
        ('{iri}', 'vm:ledBy',
            'vm:HE/person-{row[leader_staff_number].as_text}'),
        ('{iri}', 'vm:hasParentOrganization', '{parent_iri}'),
        # Present in ontology, populated via orgunit2activity transform
        # ('{iri}', 'vmhe:hasInvolvement', ''),
    ],
}
