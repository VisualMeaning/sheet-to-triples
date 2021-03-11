# use "Highways > 000 Data Ingest > 20210311 activity2itsystem v3.xlsx"
{
    'sheet': 'itsystem',
    'lets': {
        'iri': 'vm:HE/itsystem-{row[ITSystemID].as_slug}',
        'dp_iri': 'vm:/HE/deliverypartner-{row[DeliveryPartner].as_slug}'
    },
    'triples': [
        ('{iri}', 'rdf:type',
            'http://webprotege.stanford.edu/R9yHLGw3z6gILmTwQSizzdi'),
        ('{iri}', 'vm:name', '{row[Shortname].as_text}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        # possibly available via deliverypartner instead?
        ('{dp_iri}', 'vm:supports', '{iri}'),
        # columns present in sheet but unpopulated
        # ('{iri}', 'vm:ownedBy',
        #   'vm:/HE/person-{row[Person as Owner].as_slug}'),
        # ('{iri}', 'vm:managedBy',
        #   'vm:/HE/person-{row[Person as Manager].as_slug}'),
        # not present in sheet
        # ('{iri}', 'vm:sro', ''),
    ],
}
