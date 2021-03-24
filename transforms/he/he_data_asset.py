# uses 000 Data Ingest > 20210318 dataasset2itsystem.xlsx
[
    {
        'sheet': 'DataAsset',
        'lets': {
            'iri': 'vm:HE/dataasset-{row[DataAssetID].as_slug}',
        },
        'triples': [
            ('{iri}', 'rdf:type',
                'http://webprotege.stanford.edu/R9CEIYtS6EVWnP7kLOlZGYO'),
            # no Name column!
            ('{iri}', 'vm:name', '{row[DataAssetID].as_text}'),
            ('{iri}', 'vm:description', '{row[Description].as_text}'),
            # Person relationship requested but columns not populated
            # ('{iri}', 'vm:hasOwner', 'vm:HE/person-{row[Owner].as_slug}'),
            # ('{iri}', 'vm:hasManager', 'vm:HE/person-{row[Manager].as_slug}')
            # Present in ontology but not in sheet
            # provided by
            # ('{iri}',
            #   'http://webprotege.stanford.edu/RCptIcn975cERAVUlJOL7sV', '')
            # used by
            # ('{iri}',
            #   'http://webprotege.stanford.edu/RDHyoSHFDLL9G8kmD2B11GoV', '')
            # ('{iri}', 'vm:dataAccessRestrictions', ''),
            # ('{iri}', 'vm:imagesAndVideo', ''),
            # ('{iri}', 'vm:personallyIdentifiableInformation', ''),
            # ('{iri}', 'vm:sensitive', ''),
            # ('{iri}', 'vm:usedFor', ''),
        ],
    },
    {
        'sheet': 'DataAsset2itsystem',
        'lets': {
            'dataasset_iri': 'vm:HE/dataasset-{row[DataAssetID].as_slug}',
            'itsystem_iri': 'vm:HE/itsystem-{row[ITSystemID].as_slug}',
        },
        'triples': [
            # managed within
            ('{dataasset_iri}',
                'http://webprotege.stanford.edu/R8UlzVcWWjnYzxJxqtXIIFd',
                '{itsystem_iri}'),
        ],
    }
]
