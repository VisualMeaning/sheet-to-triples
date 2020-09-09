{
    'sheet': 'Map Markers',
    'lets': {
        'iri': 'vm:issues/{row[Movement Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Issue'),
        ('{iri}', 'vm:name', '{row[Movement Name]}'),
        ('{iri}', 'vm:description', '{row[Content]}'),
        ('{iri}', 'vm:hasIcon', '{row[Icon]}'),
        ('{iri}', 'vm:atGeoPoint', '{row[Coordinates].as_geo}'),
        ('{iri}', 'vm:ofStory', 'vm:stories/12'),
    ],
}
