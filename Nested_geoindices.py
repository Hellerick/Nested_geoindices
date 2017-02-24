from math import pi, cos, sin, asin, log

# Published here: http://pastebin.com/CR6zg3jT

# Adapted from
# c:\Users\User\Dropbox\Programming\Python\EarthSplitter.2016-11-11.py

alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# alpha = '0123456789'
# alpha = '0123456789abcdef'

deg = pi / 180

Earth_radius = 6371000

full_resolution = 5  # meters

y0, y1, x0, x1 = range(4)
ver, hor = range(2)


def main():
    area_from_index('PYTHON')
    area_from_index('REDDIT')
    index_from_coord(45, 11)
    index_from_coord(55.95, 92.35)


full_code_length = int(
    log(4 * pi * (Earth_radius / full_resolution) ** 2) / log(len(alpha))) + 1


def check_lines(lines, box, annotate=False):
    if annotate: print('Checking {} lines'.format(lines))
    span = [box[y1] - box[y0], box[x1] - box[x0]]
    parals = [span[ver] / lines * (i + 0.5) + box[y0] for i in range(lines)]
    if annotate: print('Parals:', ['{:.2f}'.format(p) for p in parals])
    lengths = [span[hor] * cos(i * deg) for i in parals]
    if annotate: print('Lengths:', ['{:.2f}'.format(l) for l in lengths])
    share = sum(lengths) / len(alpha)
    def divs(s):
        return [round(lengths[i] / s) for i in range(lines)]
    counter = 0
    maxshare = share * 1.5
    minshare = share / 1.5
    guesses = {
        share: divs(share),
        maxshare: divs(maxshare),
        minshare: divs(minshare),
    }
    while not len(alpha) in [sum(i) for i in guesses.values()]:
        counter += 1
        maxshare = max(i for i in guesses if sum(guesses[i]) >= len(alpha))
        minshare = min(i for i in guesses if sum(guesses[i]) <= len(alpha))
        if annotate:
            for i in guesses: print(*i)
            print(' ', maxshare, divs(maxshare), minshare, divs(minshare))
        share = (maxshare + minshare) / 2
        if share in guesses:
            if (lines % 2 == 1) and (
                        abs(sum(guesses[share]) - len(alpha)) == 1):
                guesses[share][lines // 2] = (
                    guesses[share][lines // 2] -
                    sum(guesses[share]) + len(alpha)
                )
        else:
            guesses[share] = divs(share)
    if 0 in guesses[share]:
        return guesses[share], len(alpha)
    params = [span[ver] / lines,
              *[lengths[i] / divs(share)[i] for i in range(lines)]]
    inequality = max(params) / min(params)
    if annotate:
        print(' Params', params)
        print(' Inequality {:.4f}'.format(inequality))
    return guesses[share], inequality


def split(box, annotate=False):
    # box: list of four coordinates, degrees:
    # y0, y1: bottom and top borders
    # x0, x1: left and right borders
    if annotate:
        print('Splitting {:.4f} {:.4f} {:.4f} {:.4f}'.format(*box))
    subsection_variants = [
        check_lines(lines, box)
        for lines in range(2, int(2 * len(alpha) ** .5))
        ]
    subsections = min(subsection_variants, key=lambda x: x[1])[0]
    sines = [sin(box[y0] * deg), sin(box[y1] * deg)]
    for i, s in enumerate(subsections[:-1]):
        sines = (
            sines + [
                sines[0] +
                sum(subsections[0:i + 1]) / len(alpha) * (sines[1] - sines[0])
            ]
        )
    if annotate:
        print('Chosen subsection scheme:', subsections)
    sines.sort()
    belt_borders = [asin(s) / deg for s in sines]

    if annotate:
        print('Belt borders:', belt_borders)

    zone_borders = {}
    zone_map = [[belt, zone]
                for belt, zones in enumerate(subsections)
                for zone in range(zones)]
    for i, c in enumerate(alpha):
        belt, zone = zone_map[i]
        zoneqty = subsections[belt]
        zone_borders[c] = [
            belt_borders[belt],
            belt_borders[belt + 1],
            zone / zoneqty * (box[x1] - box[x0]) + box[x0],
            (zone + 1) / zoneqty * (box[x1] - box[x0]) + box[x0],
        ]
    if annotate:
        for z in sorted([[z, zone_borders[z]] for z in zone_borders]):
            print(z)
    return zone_borders


def metric(size):  # Size in degrees
    size = [i * deg * Earth_radius for i in size]  # Now in meters
    if max(size) > 1000:
        unit = 'km'
        size = [i / 1000 for i in size]
    else:
        unit = 'm'
    if max(size) > 100:
        prec = '0'
    elif max(size) > 10:
        prec = '1'
    else:
        prec = '2'
    return ('{:4.' + prec + 'f}x{:4.' + prec + 'f} {:2}').format(*size, unit)


def index_from_coord(lat, lon, show=True):
    print('== Get nested indices for {}, {} =='.format(lat, lon))
    print(('{:'+str(full_code_length)+'s}   Latitudes Longitudes Size').format('Indices'))
    area = [-90, +90, -180, +180]
    code = ''
    while len(code) < full_code_length:
        zones = split(area)
        char = [a for a in alpha if
                zones[a][y0] <= lat <= zones[a][y1] and
                zones[a][x0] <= lon <= zones[a][x1]
                ][0]
        code = code + char
        area = zones[char]
        size = metric([(area[y1] - area[y0]), (area[x1] - area[x0]) * cos(
            (area[y1] + area[y0]) / 2 * deg)])
        if show:
            print(
                (
                    '{:' + str(full_code_length) + '} : '
                                                   '{:8.4f}~{:8.4f}, {:9.4f}~{:9.4f} ({})'
                ).format(code, *area, size)
            )
    if show: print()
    return code


def area_from_index(sought_code, show=True):
    print('== Find area for the index {} =='.format(sought_code))
    area = [-90, +90, -180, +180]
    code = ''
    while code != sought_code:
        zones = split(area)
        char = sought_code[len(code)]
        code = code + char
        area = zones[char]
        size = metric([
            (area[y1] - area[y0]),
            (area[x1] - area[x0]) * cos((area[y1] + area[y0]) / 2 * deg)
        ])
        if show:
            print(
                (
                    '{:' + str(full_code_length) + '} : '
                    '{:8.4f}~{:8.4f}, {:9.4f}~{:9.4f} ({})'
                ).format(code, *area, size)
            )
    if show:
        print(
            'Center point: {:0.4f}, {:0.4f}'.format(
                (area[y0] + area[y1]) / 2,
                (area[x0] + area[x1]) / 2
            )
        )
        print()
    return area


if __name__ == "__main__":
    main()
