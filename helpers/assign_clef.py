def clef(inst):
    clef='treble'
    if inst=='flute':
        clef='treble'
    elif inst=='alto_flute':
        clef='treble'
    elif inst=='baritone_generic':
        clef='bass'
    elif inst=='bassoon':
        clef='bass'
    elif inst=='bass_cl':
        clef='bass'
    elif inst=='bass_drum':
        clef='treble'
    elif inst=='bass_trombone':
        clef='bass'
    elif inst=='cello':
        clef='bass'
    elif inst=='clarinet':
        clef='treble'
    elif inst=='contrabassoon':
        clef='bass'
    elif inst=='crotales':
        clef='treble'
    elif inst=='double_bass':
        clef='bass'
    elif inst=='english_horn':
        clef='treble'
    elif inst=='horn':
        clef='treble'
    elif inst=='oboe':
        clef='treble'
    elif inst=='piatti':
        clef='treble'
    elif inst=='piccolo':
        clef='treble'
    elif inst=='snare':
        clef='treble'
    elif inst=='solo_cello':
        clef='bass'
    elif inst=='solo_violin':
        clef='treble'
    elif inst=='soprano_generic':
        clef='treble'
    elif inst=='tam-tam':
        clef='treble'
    elif inst=='tenor_generic':
        clef='treble'
    elif inst=='tenor_trombone':
        clef='bass'
    elif inst=='timp':
        clef='treble'
    elif inst=='tuba':
        clef='bass'
    elif inst=='viola':
        clef='alto'

    return clef