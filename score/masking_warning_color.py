def color(val):
    if val < 60:
        r = 0
        g = 255
        b = 0
    if val >= 60:
        r = ((val - 60) / 20) * 255
        g = 255
        b = 120
    if val >= 80:
        r = 255
        g = 255 - (((val - 80) / 20) * 255)
        b = 120 - (((val - 80) / 20) * 120)

    return 'rgb({},{},{})'.format(r, g, b)