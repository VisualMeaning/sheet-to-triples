{
    'data': [
        ('1_peopleplaneteconomy', 'People. Planet. Economy.', 'png'),
        ('2_systemicdysfunction', 'Systemic Dysfunction', 'png'),
        ('3_keyplayers', 'Key Players', 'png'),
        ('4_questions', 'Insightful Questions', 'png'),
        ('5a_day1diagnosis', 'Day 1: Shareholder-Primacy', 'png'),
        ('5c_day1movements', 'Day 1: Movements', 'png'),
        ('6a_day2diagnosis', 'Day 2: Performance Management', 'gif'),
        ('6c_day2movements', 'Day 2: Movements', 'png'),
        ('7a_day3diagnosis', 'Day 3: Leadership & Education', 'gif'),
        ('7c_day3movements', 'Day 3: Movements', 'png'),
        ('8_allmovements', 'The Movements', 'png'),
        ('9_leversofchange', 'Levers of Change', 'png'),
        ('10_research', 'Research, Tools & Further Reading', 'png'),
        ('3_keyplayers', 'Contact Us', 'png'),
    ],
    'lets': {
        'storyName': '{row[1]}',
        'version': '20200819',
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
