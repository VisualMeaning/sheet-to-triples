{
    'data': [{
        'view_id': 'activity',
        'geog_id': 'activity',
        'tile_id': '',
        'version': '',
        'name': 'Activity View',
        'filters': 'plottable=t&group=type',
     }, {
        'view_id': 'org',
        'geog_id': 'org',
        'tile_id': 'org',
        'version': '20210330',
        'name': 'Organisation View',
        'filters': 'a=org:OrganisationalUnit',
     }, {
        'view_id': 'org-people',
        'geog_id': 'org',
        'tile_id': 'org',
        'version': '20210330',
        'name': 'Organisation + People View',
        'filters': 'a=org:OrganisationalUnit+foaf:Person&group=org',
     }, {
        'view_id': 'cap',
        'geog_id': 'cap',
        'tile_id': 'cap',
        'version': '20210311',
        'name': 'Capability View',
        'filters': 'a=Capability',
     }],
    'lets': {
        'iri': 'vm:{row[view_id]}',
    },
    'triples': [
        ('{iri}', 'rdf:type', 'vm:View'),
        ('{iri}', 'vm:name', '{row[name]}'),
        ('{iri}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/hwx/{row[version].as_text}/'
         'overlays/{row[tile_id]}/{{z}}-{{x}}-{{y}}.png#background:#fff'),
        ('{iri}', 'vm:useFilters', '{row[filters]}'),
        ('{iri}', 'vm:asOrdinal', '{n}'),
        ('{iri}', 'vm:comment', '{row[geog_id]}'),
    ],
}
