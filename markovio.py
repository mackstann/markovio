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

# build markov chains

table = {}
for y, line in enumerate(imglines):
    for x, pixel in enumerate(line):
        above     = imglines[y-1][x] if height-1 > y > 0 else None
        left      = imglines[y][x-1] if x > 0 else None
        leftleft  = imglines[y][x-2] if x > 1 else None
        aboveleft = imglines[y-1][x-1] if above and left else None
        table.setdefault((y, above, left, aboveleft, leftleft), []).append(pixel)

# generate output

output = []

for y in range(height):
    output.append([])
    for x in range(width):
        above     = output[y-1][x] if height-1 > y > 0 else None
        left      = output[y][x-1] if x > 0 else None
        leftleft  = output[y][x-2] if x > 1 else None
        aboveleft = output[y-1][x-1] if above and left else None
        output[-1].append(random.choice(table.get((y, above, left, aboveleft, leftleft), bgpixel)))

# un-reverse only vertically -- but leave horizontal alone.  why does this work
# best?  who the hell knows?

output = output[::-1]

# write

prefix = '/tmp/markovio.out'
xpm = prefix+'.xpm'
png = prefix+'.png'

f = open(xpm, 'wr+')
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
assert 0 == subprocess.Popen([
    "convert", '-scale',
    "%dx%d" % (width*outputscale, height*outputscale),
    xpm, png
]).wait()

print open(xpm, 'r').read()
print

print "the above xpm image was written to %s and" % xpm
print "also converted to %s, scaled up %d times" % (png, outputscale)

