{
    'data': [{
        'title': 'More Info',
        'desc': '''\
**Movement:** New Economics Foundation

**Status:** Non-profit

**Mechanisms:** Policy, advocacy, community organisation

**Desired outcome:** Transform the economy so it works for people and the
planet. Specifically:
1. A new social settlement
2. The Green New Deal
3. The democratic economy

**How?**
- Producing research and policy solutions
- Supporting on-the-ground projects that devolve power to communities
- Organising and movement building
- Consultancy inc. Social Return on Investment analysis

**Key stakeholders:** Local campaigning groups, local and national government,
the EU

**Location:** United Kingdom''',
        'icon': 'info_g.png',
        'point': '[-142, 39.75]',
    }],
    'lets': {
        'iri': 'vm:issues/more-info',
        'version': '20200819',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:Issue'),
        ('{iri}', 'vm:name', '{row[title]}'),
        ('{iri}', 'vm:description', '{row[desc]}'),
        ('{iri}', 'vm:hasIcon', '{row[icon]}'),
        ('{iri}', 'vm:atGeoPoint', '{row[point]}'),
        ('{iri}', 'vm:ofStory', 'vm:stories/7'),
    ],
}
