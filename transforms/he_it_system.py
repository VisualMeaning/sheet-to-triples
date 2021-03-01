{
    'sheet': 'ITSystem',
    'lets': {
        'iri': 'vm:HE/itsystem-{row[Number]}-{row[Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type',
            'http://webprotege.stanford.edu/R9yHLGw3z6gILmTwQSizzdi'),
        ('{iri}', 'vm:name', '{row[Name].as_text}'),
        ('{iri}', 'skos:altLabel', '{row[ShortName].as_text}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
        ('{iri}', 'vm:deliveryPartner',
            'vm:HE/deliverypartner-{row[DeliveryPartner].as_slug}'),
    ],
}
