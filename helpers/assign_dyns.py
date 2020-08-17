def dyns(vel):
    if vel<70:
        dyn='p'
    elif vel<85:
        dyn='mf'
    else:
        dyn='f'
    return dyn