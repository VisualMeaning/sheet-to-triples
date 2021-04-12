{
    'book': '20210405 dataasset2itsystem2activity.xlsx',
    'sheet': 'ITSystem',
    'lets': {
        'iri': 'vm:HE/itsystem-{row[ITSystemID].as_slug}',
        'dp_iri': 'vm:HE/deliverypartner-{row[DeliveryPartner].as_slug}',
    },
    'allow_empty_subject': True,
    'non_unique': ['vm:supports'],
    'triples': [
        ('{iri}', 'rdf:type',
            'http://webprotege.stanford.edu/R9yHLGw3z6gILmTwQSizzdi'),
        ('{iri}', 'vm:name', '{row[Shortname].as_text}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        # delivery partner entity doesn't exist
        # ('{dp_iri}', 'vm:supports', '{iri}'),
        # requested properties
        ('{iri}', 'vm:deliveredBy', '{row[DeliveryPartner].as_text}'),
        ('{iri}', 'vm:vendor', '{row[Vendor].as_text}')
        # columns present in sheet but unpopulated
        # ('{iri}', 'vm:ownedBy',
        #   'vm:/HE/person-{row[Person as Owner].as_slug}'),
        # ('{iri}', 'vm:managedBy',
        #   'vm:/HE/person-{row[Person as Manager].as_slug}'),
        # not present in sheet
        # ('{iri}', 'vm:sro', ''),
    ],
}
