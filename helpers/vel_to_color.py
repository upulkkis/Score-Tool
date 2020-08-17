def color(vel):
    color='rgb(160, 160, 160)'
    if vel<70:
        color='rgb(80, 80, 80)'
    elif vel>85:
        color='black'
    return color