
{
    'sheet': 'DeliveryPartner',
    'lets': {
        'iri': 'vm:HE/deliverypartner-{row[Number]}-{row[Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type',
            'http://webprotege.stanford.edu/RCnRceKsHZf8Gt9UvDjM6We'),
        ('{iri}', 'vm:name', '{row[Name].as_text}'),
        ('{iri}', 'skos:altLabel', '{row[ShortName].as_text}'),
        ('{iri}', 'vm:description', '{row[Description].as_text}'),
    ],
}
