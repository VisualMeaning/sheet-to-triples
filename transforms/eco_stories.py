{
    'data': [
        ('00_welcome', 'Welcome', 'png'),
        ('01_peopleplaneteconomy', 'People. Planet. Economy.', 'png'),
        ('02_systemicdysfunction', 'A System in Crisis', 'png'),
        ('03_keyplayers', 'Economic Actors', 'png'),
        ('04_insights', 'Key Insights', 'png'),
        ('05_d1shareholderprimacy', 'Diagnosis 1: Shareholder-Primacy', 'png'),
        ('06_movements_shareholderprimacy', 'Diagnosis 1: Movements', 'png'),
        ('07_d2performance', 'Diagnosis 2: Corporate Performance Management', 'gif'),
        ('08_movements_performance', 'Diagnosis 2: Movements', 'png'),
        ('09_d3leadership', 'Diagnosis 3: Leadership & Education', 'gif'),
        ('10_movements_leadership', 'Diagnosis 3: Movements', 'png'),
        ('11_allmovements', 'The Movements Landscape', 'png'),
        ('12_leversofchange', 'Incorporating Purpose: Levers of Change', 'png'),
        ('13_furtherreading', 'Research, Tools & Further Reading', 'png'),
        ('14_contactus', 'Contact Us', 'png'),
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
    },
    'triples': [
        ('{query[story]}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/economicsystem/{version}/'
            'overlays/{row[0]}/{{z}}-{{x}}-{{y}}.{row[2]}'),
    ],
}
