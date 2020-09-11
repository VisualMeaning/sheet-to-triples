{
    'data': [
        ('00_welcome', 'Home', '#background:black'),
    ],
    'lets': {
        'storyName': '{row[1]}',
        'version': '20200907',
    },
    'queries': {
        'story': (
            'select ?s where {'
            ' ?s rdf:type vm:Story .'
            ' ?s vm:name ?storyName .'
            '}'),
        'first': (
            'select ?p where {'
            ' ?story vm:firstPoint ?p .'
            '}'),
    },
    'triples': [
        ('{story}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/economicsystem/{version}/'
            'overlays/{row[0]}/{{z}}-{{x}}-{{y}}.png{row[2]}'),
        ('{first}', 'vm:minGeoPoint', '[-512,-256]'),
        ('{first}', 'vm:maxGeoPoint', '[256,512]'),
    ],
}
