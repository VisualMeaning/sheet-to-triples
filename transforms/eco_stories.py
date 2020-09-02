{
    'data': [
        ('1_peopleplaneteconomy', 'People. Planet. Economy.'),
        ('2_systemicdysfunction', 'Systemic Dysfunction'),
        ('3_keyplayers', 'Key Players'),
        ('4_questions', 'Insightful Questions'),
        ('5a_day1diagnosis', 'Day 1: Shareholder-Primacy'),
        ('5c_day1movements', 'Day 1: Movements'),
        ('6a_day2diagnosis', 'Day 2: Performance Management'),
        ('6c_day2movements', 'Day 2: Movements'),
        ('7a_day3diagnosis', 'Day 3: Leadership & Education'),
        ('7c_day3movements', 'Day 3: Movements'),
        ('8_allmovements', 'The Movements'),
        ('9_leversofchange', 'Levers of Change'),
        ('10_research', 'Research, Tools & Further Reading'),
        ('3_keyplayers', 'Contact Us'),
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
            'overlays/{row[0]}/{{z}}-{{x}}-{{y}}.png'),
    ],
}
