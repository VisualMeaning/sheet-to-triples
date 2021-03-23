# uses Highways > 000 Data Ingest > 20210323 performance measures.xlsx

# defines properties and relationships for the following classes:
# * Desired Result (which may be assessed by many Performance Measures)
# * Performance Measure (which may be measured by many Recorded Measures)
# * Recorded Measure (which may link to many Single Recorded Measures)
# * Single Recorded Measure
# * Unit
[
    {
        'sheet': 'PM Results',
        'non_unique': ['vm:hasRecordedMeasure'],
        'lets': {
            'rec_iri': 'vm:HE/{row[PM number (VM)].as_slug}',
            'ind_rec_iri': ('vm:HE/{row[PM number (VM)].as_slug}'
                            '-{row[Time of measure].as_slug}'
                            '-{row[Date of measure].as_date_or_text}'),
            'unit_iri': 'vm:HE/unit-{row[Unit of measure].as_slug}',
        },
        # define 3 classes from this sheet
        'triples': [
            # Recorded Measure - this is an object to attach Single Recorded
            # Measures to, there will be many dupes that get deduped later
            ('{rec_iri}', 'rdf:type', 'vm:RecordedMeasure'),
            ('{rec_iri}', 'vm:name', '{row[PM Title].as_text}'),
            ('{rec_iri}', 'vm:hasRecord', '{ind_rec_iri}'),
            # Single Recorded Measure - an invented class containing data for
            # a single record of the Recorded Measure at a fixed point in time
            ('{ind_rec_iri}', 'rdf:type', 'vm:SingleRecordedMeasure'),
            ('{ind_rec_iri}', 'vm:name',
                ('{row[PM Title].as_text} - '
                 '{row[Time of measure].as_text} '
                 '{row[Date of measure].as_date_or_text}')),
            ('{ind_rec_iri}', 'vm:records', '{row[Measure].as_text}'),
            ('{ind_rec_iri}', 'vm:takenAt',
                '{row[Date of measure].as_date_or_text}'),
            ('{ind_rec_iri}', 'vm:timeOfMeasure',
                '{row[Time of measure].as_text}'),
            ('{ind_rec_iri}', 'vm:measuredIn',
                'vm:HE/unit-{row[Unit of measure].as_slug}'),
            # Unit
            ('{unit_iri}', 'rdf:type', 'vm:Unit'),
            ('{unit_iri}', 'vm:name', '{row[Unit of measure].as_text}'),
        ],
    },
    {
        'sheet': 'Performance Measures (PM)',
        'lets': {
            'rec_iri': 'vm:HE/{row[PM number (VM)].as_slug}',
        },
        'triples': [
            ('{rec_iri}', 'vm:description', '{row[Description].as_text}'),
        ],
    },
    {
        # This data model is a bit confusing - in the hierarchy of data the
        # sheet's concept of a Metric actually occupies the corresponding
        # position of the ontology's Performance Measure, and the sheet's
        # Performance Measure is an ontology Recorded Measure
        'sheet': 'Metrics2PM ',
        'non_unique': ['vm:measures', 'vm:hasRecordedMeasure'],
        'lets': {
            'pm_iri': 'vm:HE/{row[MET number (VM)].as_slug}',
            'rec_iri': 'vm:HE/{row[Linked to PM number].as_slug}',
            'dr_iri': ('vm:HE/{row[Performance Specification / Desired Result]'
                       '.as_slug}')
        },
        'triples': [
            # Desired Result - this should link up with top level definitions
            # from the AI export
            ('{dr_iri}', 'rdf:type', 'vm:DesiredResult'),
            ('{dr_iri}', 'vm:name',
                '{row[AI_desired_result].as_text}'),
            ('{pm_iri}', 'rdf:type',
                'http://webprotege.stanford.edu/Rr60siMdu9IEvdag4DhF7M'),
            ('{pm_iri}', 'vm:name', '{row[Title].as_text}'),
            ('{pm_iri}', 'vm:hasRecordedMeasure', '{rec_iri}'),
            ('{pm_iri}', 'vm:measures', '{dr_iri}'),
            # Not in sheet
            # Customer (subclass of Orgunit)
            # ('{iri}', 'vm:providesValueTo', ''),
            # Stakeholder (subclass of Orgunit)
            # ('{iri}', 'vm:ofInterestTo', ''),
        ],
    },
    {
        'sheet': 'HE Metrics',
        'allow_empty_subject': True,
        'lets': {
            'pm_iri': 'vm:HE/{row[MET number (VM)].as_slug}'
        },
        'triples': [
            ('{pm_iri}', 'vm:description', '{row[Description]}'),
        ],
    },
    {
        # Can link from PM to activity but not from Desired Result to activity
        # as the ontology specifies
        'sheet': 'Metric_2_activity',
        'lets': {
            'pm_iri': 'vm:HE/{row[MET number (VM)].as_slug}',
            'activity_iri': 'vm:HE/{row[Activity].as_slug}'
        },
        'triples': [
            ('{activity_iri}', 'vm:leadsTo', '{pm_iri}'),
        ],
    }
]
