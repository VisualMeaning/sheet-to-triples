{
    'data': [
        ('01_internalmodel', 'Internal Model'),
        ('02_keyquestions', 'Key Questions'),
        ('03_interventions', 'Potential Interventions'),
        ('04_stakeholders', 'Stakeholders'),
        ('05_currentprojects', 'Current Projects'),
    ],
    'lets': {
        'storyName': '{row[1]}',
        'version': '20200922',
    },
    'queries': {
        'story': (
            'select ?s where {'
            ' ?s rdf:type vm:Story .'
            ' ?s vm:name ?storyName .'
            '}'),
    },
    'triples': [
        ('{story}', 'vm:usesMapTiles',
            'https://opatlas-live.s3.amazonaws.com/highways_internal_model/{version}/'
            'overlays/{row[0]}/{{z}}-{{x}}-{{y}}.png'),
    ],
}
