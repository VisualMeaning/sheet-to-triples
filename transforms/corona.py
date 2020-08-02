{
    'sheet': 'Coronavirus_v2',
    'lets': {
        'iri': 'vm:issues/{row[Title].as_slug}',
        'stakeholderName': '{row[Stakeholder]}',
        'assets': 'TODO/',
    },
    'queries': {
        'stakeholder': (
            'select ?s where {'
            ' ?s rdf:type vm:Stakeholder .'
            ' ?s vm:name ?stakeholderName .'
            '}'),
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Issue'),
        ('{iri}', 'vm:name', '{row[Title]}'),
        ('{iri}', 'vm:description', '{row[Text]}'),
        ('{iri}', 'vm:ofStakeholder', '{query[stakeholder]}'),
        ('{iri}', 'vm:geoPointOf', '{row[Coordinates].as_geo}'),
        ('{iri}', 'vm:hasIcon', '{assets}{row[Icon]}'),
    ],
}
