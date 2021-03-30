{
    'book': '20210330 dataasset2itsystem2activity.xlsx',
    'sheet': 'ITSystem',
    'lets': {
        'iri': 'vm:HE/itsystem-{row[ITSystemID].as_slug}',
        'dp_iri': 'vm:HE/deliverypartner-{row[DeliveryPartner].as_slug}',
    },
    'allow_empty_subject': True,
    'non_unique': ['vm:supports'],
    'triples': [
        ('{iri}', 'rdf:type', 'http://webprotege.stanford.edu/ItSystem'),
        ('{iri}', 'vm:name', '{row[Shortname].as_text}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        # possibly available via deliverypartner instead?
        ('{dp_iri}', 'vm:supports', '{iri}'),
        # requested properties
        ('{iri}', 'vm:deliveredBy', '{dp_iri}'),
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
