from fuzzywuzzy import process

def value_to_color(value):
    return 'rgb({}, 0, 0)'.format(value)

def set_name(number, name, instruments):
    inst_name = 'violin'
    name=name.lower()

    certainty = 90

    if name.find('fagot')>=0:
        inst_name = 'bassoon'
    elif name.find('contrabass')>=0:
        inst_name = 'double_bass'
    elif name.find('vcl')>=0:
        inst_name = 'cello'
    elif name.find('basso')>=0:
        inst_name = 'double_bass'
    elif name.find('cymbal')>=0:
        inst_name = 'piatti'
    elif name.find('choir')>=0:
        inst_name = 'soprano_generic'
    elif name.find('violinsolo')>=0:
        inst_name = 'solo_violin'
    elif name.find('viol1')>=0:
        inst_name = 'violin'
    elif name.find('viol2')>=0:
        inst_name = 'violin'
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
    else:
        inst_name, certainty = process.extractOne(name, instruments)

    if inst_name.find('bass_trombone')>=0:
        inst_name = 'tenor_trombone'

    return inst_name, certainty
