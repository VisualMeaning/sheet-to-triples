{
    'sheet': 'Map Markers',
    'lets': {
        'iri': 'vm:issues/{row[Marker Name].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Issue'),
        ('{iri}', 'vm:name', '{row[Marker Name]}'),
        ('{iri}', 'vm:description', '### {row[Marker Name]}\n{row[Content]}'),
        ('{iri}', 'vm:hasIcon', '{row[Icon]}'),
        ('{iri}', 'vm:atGeoPoint', '{row[Coordinates].as_geo}'),
        ('{iri}', 'vm:ofStory', 'vm:stories/13'),
    ],
}
