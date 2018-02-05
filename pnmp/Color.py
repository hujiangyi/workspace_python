import random
def colorArray(count):
    colors = []
    for i in range(0,count) :
        colorStr = '#%02X%02X%02X' % (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        colors.append(colorStr)
    return colors