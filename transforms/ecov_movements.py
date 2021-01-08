{
    'sheet': 'Map Markers',
    'lets': {
        'iri': 'vm:issues/{row[Movement Name].as_slug}',
        'category': 'vm:category/{row[Category].as_slug}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Issue'),
        ('{iri}', 'vm:name', '{row[Movement Name]}'),
        ('{iri}', 'vm:description', '''\
**Influence strategies:** {row[Strategies]}

**Key stakeholders:** {row[Key stakeholders]}

**Mission:** {row[Mission]}

**How?**
{row[How]}

**Geographic remit:** {row[Geo Remit]}

[Website]({row[Link]})'''),
        ('{iri}', 'vm:hasIcon', 'info_g.png'),
        ('{iri}', 'vm:atGeoPoint', '{row[Coordinates].as_geo}'),
        ('{iri}', 'vm:hasAspect', 'none'),
        ('{iri}', 'vm:hasCategory', '{category}'),
        ('{category}', 'rdf:type', 'vm:Category'),
        ('{category}', 'vm:name', '{row[Category]}'),
        ('{iri}', 'vm:ofStory', 'vm:story-11_allmovements'),
    ],
}
