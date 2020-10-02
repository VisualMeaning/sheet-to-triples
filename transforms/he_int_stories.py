{
    'data': [
        ('001_internalmodel', 'Internal Model'),
        ('002_keyquestions', 'Key Questions'),
        ('003_interventions', 'Potential Interventions'),
        ('011_foundation', 'Foundation Layer Draft'),
        ('011a_HE_orgstructure', 'HE Organisational Structure'),
        ('011b_HE_governance', 'HE Governance'),
        ('011c_HE_transprogrammes', 'HE Transformation Programmes'),
        ('011d_it_systems', 'HE IT Systems'),
        ('021_itd', 'ITD'),
        ('022_data_digital', 'Data & Digital'),
        ('023_architecture', 'Architecture, Design & Technology Services'),
        ('024_cybersec', 'Cyber Security & Information Rights'),
        ('025_infrastructure', 'Infrastructure & Platforms'),
        ('026_serviceops', 'Service Operations'),
        ('027_programmes', 'Programme Delivery'),
        ('028_strategy', 'Strategy, Transformation & Performance'),
        ('031_sp', 'Strategy & Planning'),
        ('041_ses', 'Safety, Engineering & Standards'),
        ('051_mp', 'Major Projects'),
        ('061_ops', 'Operations'),
        ('071_corp_comms', 'Corporate Affairs & Communnications'),
        ('081_general_counsel', 'General Counsel'),
        ('091_commercial', 'Commercial & Procurement'),
        ('101_finance', 'Finance'),
        ('111_hr_od', 'Human Resources & Organisational Development'),
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
            'https://opatlas-live.s3.amazonaws.com/highways_internal_model/'
            '{version}/overlays/{row[0]}/{{z}}-{{x}}-{{y}}.png'),
    ],
}
