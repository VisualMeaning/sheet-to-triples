{
    'data': [{
        'view_id': 'pavements_risk_map',
        'name': 'Pavements: Risk Map',
        'geog_id': 'pavements_risk_map',
        'filters': '',
        'class': 'View',
    }],
    'lets': {
        'iri': 'vm:view_{row[view_id]}',
        'version': '20210330',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:{row[class]}'),
        ('{iri}', 'vm:name', '{row[name]}'),
        ('{iri}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/ris3-renewals/{version}/'
            'overlays/{row[geog_id]}/{{z}}-{{x}}-{{y}}.png#background:#fff'),
        ('{iri}', 'vm:useFilters', '{row[filters]}'),
        ('{iri}', 'vm:asOrdinal', '{n}'),
        ('{iri}', 'vm:comment', '{row[geog_id]}'),
    ],
}
