#!/usr/bin/env python

import subprocess, sys, re, random, pprint, tempfile

infile = open(sys.argv[1] if len(sys.argv) > 1 else 'input.xpm')

# change these according to your input image, if needed
width = 200
height = 14
bgpixel = ' '

# the output png should be scaled up, otherwise it's tiny tiny
outputscale = 8

lines = filter(None, infile.readlines())

# reversed because building from bottom to top and right to left works better
header = lines[:-14]
imglines = list(reversed([ l.lstrip('"')[:200] for l in lines[-14:] ]))

def adjacent(data, x, y):
    above     = data[y-1][x] if height-1 > y > 0 else None
    left      = data[y][x-1] if x > 0 else None
    leftleft  = data[y][x-2] if x > 1 else None
    aboveleft = data[y-1][x-1] if above and left else None
    return above, left, leftleft, aboveleft

# build markov chains

table = {}

for y, line in enumerate(imglines):
    for x, pixel in enumerate(line):
        key = (y,) + adjacent(imglines, x, y)
        table.setdefault(key, []).append(pixel)

# generate output

output = []

for y in range(height):
    output.append([])
    for x in range(width):
        key = (y,) + adjacent(output, x, y)
        output[-1].append(random.choice(table.get(key, bgpixel)))

# un-reverse only vertically -- but leave horizontal alone.  why does this work
# best?  who the hell knows?

output = output[::-1]

# write

prefix = '/tmp/markovio.out'
xpm = prefix+'.xpm'
png = prefix+'.png'

f = open(xpm, 'w')
f.write(''.join(header))

for y in range(height):
    f.write('"')
    for x in range(width):
        f.write(output[y][x])
    f.write('"')

    if y < height-1:
        f.write(',\n')
    else:
        f.write('};')

f.close()

print open(xpm, 'r').read()
print
sys.stdout.write("the above xpm image was written to %s" % xpm)

try:
    subprocess.Popen([
        "convert", '-scale',
        "%dx%d" % (width*outputscale, height*outputscale),
        xpm, png
    ]).wait()
except OSError:
    print ",\nalthough conversion from xpm to png didn't work."
    print "do you have the 'convert' utility installed (from imagemagick)?"
else:
    print " and\nalso converted to %s, scaled up %d times" % (png, outputscale)


