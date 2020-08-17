def set_name(number, name):
    inst_name = 'violin'
    if name.find('solo')>0:
        inst_name = 'solo_violin'
    elif number == 41 - 1:
        inst_name = 'violin'
    elif number == 42 - 1:
        inst_name = 'viola'
    elif number == 43 - 1:
        inst_name = 'cello'
    elif number == 44 - 1:
        inst_name = 'double_bass'
    elif number == 48 - 1:
        inst_name = 'timp'
    elif number == 74 - 1:
        inst_name = 'flute'
    elif number == 57 - 1:
        inst_name = 'trumpet'
    elif number == 58 - 1:
        inst_name = 'tenor_trombone'
    elif number == 59 - 1:
        inst_name = 'tuba'
    elif number == 61 - 1:
        inst_name = 'horn'
    elif number == 69 - 1:
        inst_name = 'oboe'
    elif number == 70 - 1:
        inst_name = 'english_horn'
    elif number == 71 - 1:
        inst_name = 'bassoon'
    elif number == 72 - 1:
        inst_name = 'clarinet'
    elif number == 73 - 1:
        inst_name = 'piccolo'
    elif number == 14 - 1:
        inst_name = 'xylophone'
    elif number == 53 - 1:
        inst_name = 'soprano_generic'
    elif number == 54 - 1:
        inst_name = 'soprano_generic'

    if name.find('viola')>=0:
        inst_name = 'viola'
    elif name.find('cello')>=0:
        inst_name = 'cello'
    elif name.find('contrabassoon')>=0:
        inst_name = 'contrabassoon'
    elif name.find('fagot')>=0:
        inst_name = 'bassoon'
    elif name.find('contrabass')>=0:
        inst_name = 'double_bass'
    elif name.find('double')>=0:
        inst_name = 'double_bass'
    elif name.find('basso')>=0:
        inst_name = 'double_bass'

    return inst_name
