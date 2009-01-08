import subprocess, sys, re, random, pprint, tempfile

# pipe in an xpm that's 200x14.  change bgpixel if the sky background color is
# not the space character in your xpm.

infile = open(sys.argv[1] if len(sys.argv) > 1 else '5-2.pixels.xpm')

width = 200
height = 14
bgpixel = ' '
outputscale = 8

lines = filter(None, infile.readlines())

# reversed because building from bottom to top and right to left works better
header = lines[:-14]
imglines = list(reversed([ l.lstrip('"')[:200] for l in lines[-14:] ]))

# build markov chains

table = {}
for y, line in enumerate(imglines):
    for x, pixel in enumerate(line):
        above = imglines[y-1][x] if height-1 > y > 0 else None
        left  = imglines[y][x-1] if x > 0 else None
        aboveleft = imglines[y-1][x-1] if above and left else None
        table.setdefault((y, above, left, aboveleft), []).append(pixel)

# generate output

output = []

for y in range(height):
    output.append([])
    for x in range(width):
        above = output[y-1][x] if height-1 > y > 0 else None
        left  = output[y][x-1] if x > 0 else None
        aboveleft = output[y-1][x-1] if above and left else None
        output[-1].append(random.choice(table.get((y, above, left, aboveleft), bgpixel)))

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
subprocess.Popen([
    "convert", '-scale',
    "%dx%d" % (width*outputscale, height*outputscale),
    xpm, png
])

print open(xpm, 'r').read()
print

print "the above xpm image was written to %s and" % xpm
print "also converted to %s, scaled up %d times" % (png, outputscale)

