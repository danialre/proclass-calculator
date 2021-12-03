### pax.py
import os
import pandas

from collections import namedtuple

BASE_URL = "https://www.solotime.info/pax/rtp{year}.html"
Driver = namedtuple('Driver', 'sccaclass,number,driver,time,penalties')

def save_pax(paxdata, year):
    # cache pax data so we don't bombard solotime with queries
    with open(f'pax/{year}.txt', 'w') as paxf:
        for classname in paxdata:
            paxf.write(f"{classname} {paxdata[classname]:.3f}\n")

def read_pax(year):
    # read pax data from a local copy
    paxdata = {}
    with open(f'pax/{year}.txt') as paxf:
        for line in paxf.readlines():
            line = line.split()
            paxdata[line[0]] = float(line[1])
    return paxdata

def get_pax(year):
    # get (download or read) PAX data for a particular year
    if not os.path.exists(f"pax/{year}.txt"):
        # no cached data available, get data from solotime.info
        print(f"Accessing {BASE_URL.format(year=year)}")
        tables = pandas.read_html(BASE_URL.format(year=year))
        # first table is PAX data, iterate over columns and rows
        pax = {}
        classname = None
        for row in tables[0].itertuples():
            for item in row:
                if isinstance(item, str):
                    # this item is a string, must be a class name
                    classname = item.lower()
                elif float(item) <= 1.0 and classname:
                    # if class name is set, next item is always the multiplier
                    pax[classname] = float(item)
                    classname = None
        save_pax(pax, year)

    return read_pax(year)

def fastest(results, year, pax=True):
    # for every event result, get the fastest non-DNF times for each driver
    if pax and isinstance(pax, bool):
        pax = get_pax(year)

    # compute fastest time per driver
    paxed = {}
    for pe, result in enumerate(results, start=1):
        paxed[pe] = []
        try:
            for index, row in result.iterrows():
                fastest = None
                penalty = None
                # check first three runs only (nationals style)
                for run in [row["Run 1.."], row["Run 2.."], row["Run 3.."]]:
                    if pandas.isna(run):
                        continue # no recorded time

                    time = run.split('+')
                    cones = 0
                    if len(time) > 1:
                        time[1] = time[1].lower()
                        # penalty detected, apply
                        if time[1] == 'dnf' and not penalty and not fastest:
                            penalty = 'dnf'
                            continue    # no time set, so set penalty as DNF and move on
                        elif time[1] == 'dnf':
                            continue    # DNF run with an existing time, skip
                        elif not time[1]:
                            time = float(time[0])   # there is a plus but no actual penalty, skip
                        else:
                            # otherwise add cone penalties to time
                            cones = int(time[1])
                            time = float(time[0]) + 2 * cones
                    else:
                        time = float(time[0])   # clean time!
                    if not fastest or time < fastest:
                        # new faster time, apply it
                        fastest = time
                        penalty = (cones if cones > 0 else None)
                if isinstance(fastest, float) and pax:
                    # apply PAX multiplier if enabled
                    try:
                        # round times to the thousandth, and look for class (without ladies designation)
                        fastest = round(fastest * pax[row["Class"].lower().replace('l', '')], 3)
                    except KeyError:
                        print(f"Warning: could not find class \"{row['Class']}\" ({row['Driver']}) for PE {pe}")
                        pass    # couldn't find the class (fake class??), so don't adjust time
                paxed[pe].append(Driver(row["Class"], row["#"], row["Driver"], fastest, penalty))
        except:
            print(f'Exception for PE {pe}')
            raise

        # sort so fastest time per event is first
        paxed[pe].sort(key=lambda k: 999.9 if k.time is None else k.time)
    return paxed
