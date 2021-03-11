{
    'sheet': 'ITSystem',
    'lets': {
        'iri': 'vm:HE/{row[ITSystemID].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type',
            'http://webprotege.stanford.edu/R9yHLGw3z6gILmTwQSizzdi'),
        ('{iri}', 'vm:name', '{row[Shortname].as_text}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:deliveryPartner',
            'vm:HE/deliverypartner-{row[DeliveryPartner].as_slug}'),
    ],
}
