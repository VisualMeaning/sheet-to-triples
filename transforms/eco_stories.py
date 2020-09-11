{
    'data': [
        # 'Home' is in eco_home transform
        ('01_peopleplaneteconomy', 'People. Planet. Economy.'),
        ('02_systemicdysfunction', 'A System in Crisis'),
        ('03_keyplayers', 'Economic Actors'),
        # 'Open Questions' is in eco_storypoints transform
        ('05_d1shareholderprimacy', 'Diagnosis 1: Shareholder-Primacy'),
        ('06_movements_shareholderprimacy', 'Diagnosis 1: Movements'),
        ('07_d2performance', 'Diagnosis 2: Corporate Performance Management'),
        ('08_movements_performance', 'Diagnosis 2: Movements'),
        ('09_d3leadership', 'Diagnosis 3: Leadership & Education'),
        ('10_movements_leadership', 'Diagnosis 3: Movements'),
        ('11_allmovements', 'The Movements Landscape'),
        ('12_leversofchange', 'Incorporating Purpose: Levers of Change'),
        ('13_furtherreading', 'Research & Further Reading'),
        ('14_contactus', 'Give Feedback'),
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
            'overlays/{row[0]}/{{z}}-{{x}}-{{y}}.png'),
        ('{first}', 'vm:minGeoPoint', '[-230,-15]'),
        ('{first}', 'vm:maxGeoPoint', '[-5,265]'),
    ],
}
