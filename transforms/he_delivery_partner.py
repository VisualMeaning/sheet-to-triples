
{
    'sheet': 'DeliveryPartner',
    'lets': {
        'iri': 'vm:HE/deliverypartner-{row[Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type',
            'http://webprotege.stanford.edu/RCnRceKsHZf8Gt9UvDjM6We'),
        ('{iri}', 'vm:name', '{row[Name].as_text}'),
        ('{iri}', 'skos:altLabel', '{row[ShortName].as_text}'),
        ('{iri}', 'vm:comment', '{row[Description].as_text}'),
    ],
}
