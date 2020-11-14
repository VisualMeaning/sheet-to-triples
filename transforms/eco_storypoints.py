{
    'data': [{
        'tiles': '04a_insight1',
        'name': 'Open Questions',
        'path': 'vm:firstPoint',
    }, {
        'tiles': '04b_insight2',
        'name': 'Open Questions',
        'path': 'vm:firstPoint / vm:followedBy',
    }, {
        'tiles': '04c_insight3',
        'name': 'Open Questions',
        'path': 'vm:firstPoint / vm:followedBy / vm:followedBy',
    }],
    'lets': {
        'storyName': '{row[name]}',
        'storyPath': '{row[path]}',
        'version': '20200907',
    },
    'queries': {
        'story': (
            'select ?s where {'
            ' ?s rdf:type vm:Story .'
            ' ?s vm:name ?storyName .'
            '}'),
        'storypoint': (
            'select ?p where {'
            ' ?story ?storyPath ?p .'
            '}'),
    },
    'triples': [
        ('{story}', 'vm:asOrdinal', '3.5'),
        ('{storypoint}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/economicsystem/{version}/'
            'overlays/{row[tiles]}/{{z}}-{{x}}-{{y}}.png'),
        ('{storypoint}', 'vm:minGeoPoint', '[-280,-15]'),
        ('{storypoint}', 'vm:maxGeoPoint', '[-5,265]'),
    ],
}
