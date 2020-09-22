{
    'sheet': 'Map Markers',
    'lets': {
        'iri': 'vm:issues/{row[Name].as_slug}',
        'storyName': '{row[Story]}',
    },
    'queries': {
        'story': (
            'select ?s where {'
            ' ?s rdf:type vm:Story .'
            ' ?s vm:name ?storyName .'
            '}'),
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Issue'),
        ('{iri}', 'vm:name', '{row[Name]}'),
        ('{iri}', 'vm:description', '{row[Description]}'),
        ('{iri}', 'vm:atGeoPoint', '{row[Coordinates].as_geo}'),
        ('{iri}', 'vm:hasIcon', '{row[Icon]}'),
        ('{iri}', 'vm:hasAspect', '{row[Text Position]}'),
        ('{iri}', 'vm:ofStory', 'vm:stories/{story}'),
    ],
}
