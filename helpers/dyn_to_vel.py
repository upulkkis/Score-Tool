def to_vel(dyn):
    vel=80
    if dyn=='p':
        vel=40
    elif dyn=='mf':
        vel=80
    elif dyn=='f':
        vel=100
    return vel