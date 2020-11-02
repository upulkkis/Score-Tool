def color(val):
    if val < 50:
        r = 0
        g = 255
        b = 0
    #if val >= 160:
    #    r = ((val - 60) / 20) * 255
    #    g = 255
    #    b = 120
    elif val >= 50:
        r = 255
        g = 200 - (((val - 50) / 50) * 200)
        b = 0 #100 - (((val - 50) / 50) * 100)

    return 'rgb({},{},{})'.format(r, g, b)