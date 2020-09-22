{
    'data': [
        ('11_corona', '2'),
        ('12_cities', '3'),
    ],
    'lets': {
        'story': 'vm:stories/{row[1]}',
        'version': '140920',
    },
    'triples': [
        ('{story}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/PetcareChina/{version}/'
            'overlays/{row[0]}/{{z}}-{{x}}-{{y}}.png'),
    ],
}
