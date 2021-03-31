# uses 000 Data Ingest > 20210318 dataasset2itsystem.xlsx
[
    {
        'book': '20210331 dataasset2itsystem2activity.xlsx',
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
            ('{iri}', 'vm:hasManager', 'vm:HE/person-{row[Staff].as_slug}'),
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
        'book': '20210331 dataasset2itsystem2activity.xlsx',
        'sheet': 'DataAsset2itsystem',
        'lets': {
            'dataasset_iri': 'vm:HE/dataasset-{row[DataAssetID].as_slug}',
        },
        'triples': [
            # managed within
            ('{dataasset_iri}',
                'http://webprotege.stanford.edu/R8UlzVcWWjnYzxJxqtXIIFd',
                'vm:HE/itsystem-{row[ITSystemID].as_slug}'),
        ],
    },
    {
        'book': '20210331 dataasset2itsystem2activity.xlsx',
        'sheet': 'DataAsset2Activity',
        'lets': {
            'iri': 'vm:HE/{row[DataAsset].as_slug}-{row[ActivityID].as_slug}',
            'parent_iri': 'vm:HE/dataasset-{row[DataAsset].as_slug}',
        },
        'allow_empty_subject': True,
        'non_unique': ['vm:hasInvolvement'],
        'triples': [
            ('{iri}', 'rdf:type', 'vm:ActivityInvolvement'),
            # ('{iri}', 'vm:name',
            #     '{row[DataAsset].as_slug}-{row[ActivityID].as_slug}'),
            ('{parent_iri}', 'vm:hasInvolvement',
                'vm:HE/{row[DataAsset].as_slug}-{row[ActivityID].as_slug}'),
            ('{iri}', 'vm:relatesTo', 'vm:HE/{row[ActivityID].as_slug}',),
            ('{iri}', 'vm:activeLabel', '{row[ActiveInvolvement].as_text}'),
            ('{iri}', 'vm:passiveLabel', '{row[PassiveInvolvement].as_text}'),
            ('{iri}', 'vm:level', '{row[% Level].as_text}'),
            ('{iri}', 'vm:primary', '{row[Primary].as_text}'),
        ],
    }
]
