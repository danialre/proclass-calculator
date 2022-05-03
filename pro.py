#!/usr/bin/env python
### pro.py
import argparse
import parser
import pax
from datetime import datetime
from os import path, mkdir

def write_results(results, year, min_events=0):
    # make sure year folder is created
    if not path.exists(path.join("results", str(year))):
        mkdir(path.join("results", str(year)))
    # save results to a csv file
    for event in results.keys():
        with open(path.join("results", str(year), f"pe{event}.csv"), 'w') as csvf:
            csvf.write("Position,Class,Number,Driver,Fastest Time (inc. cones),Penalties\n")
            for position, result in enumerate(results[event], start=1):
                # fix drivernames so there's no comma
                csvf.write(f"{position},{result.sccaclass},{result.number},{result.driver},{result.time},{result.penalties}\n")

    # also write season standings
    with open(path.join("results", str(year), "year.csv"), 'w') as csvf:
        overall = season(results, min_events=min_events)
        csvf.write(f"Position,Driver,Total Points (top {min_events}),Avg Points (top {min_events}),Total Points,Avg Points,Events\n")
        for position, driver in enumerate(overall, start=1):
            csvf.write(f"{position},{driver[0]},{driver[1]},{driver[2]},{driver[3]},{driver[4]},{driver[5]}\n")

    # just for fun, also generate one sorted by average points instead of total points
    with open(path.join("results", str(year), "year-average.csv"), 'w') as csvf:
        overall = season(results, min_events=min_events, sort_avg=True)
        csvf.write(f"Position,Driver,Total Points (top {min_events}),Avg Points (top {min_events}),Total Points,Avg Points,Events\n")
        for position, driver in enumerate(overall, start=1):
            csvf.write(f"{position},{driver[0]},{driver[1]},{driver[2]},{driver[3]},{driver[4]},{driver[5]}\n")

def season(results, min_events=0, sort_avg=False):
    # calculate season standings

    # first, collect times for all drivers relative to fastest time
    overall_points = {}
    for pe in results.keys():
        # calculate time against fastest driver
        fastest = None
        for driver in results[pe]:
            if not driver.time:
                continue # no valid time for this driver

            if not fastest:
                fastest = driver
            pct = (fastest.time / driver.time) * 100
            overall_points.setdefault(driver.driver, []).append(pct)

    # second, calculate average of all events if there is no minimum, and calculate total based on minimum events
    avg_points = []
    for driver in overall_points:
        # sort times in descending order (best times first) for each driver
        overall_points[driver].sort(reverse=True)

        # choose either the number of events driven up to the cutoff, or all events driven
        num_events_cutoff = min(len(overall_points[driver]), min_events) if min_events else len(overall_points[driver])
        total_cutoff = sum(overall_points[driver][:num_events_cutoff])
        avg_cutoff = total_cutoff / len(overall_points[driver][:num_events_cutoff])
        # also calculate totals without cutoffs
        total = sum(overall_points[driver])
        avg = total / len(overall_points[driver])
        avg_points.append((driver, total_cutoff, avg_cutoff, total, avg, len(overall_points[driver])))

    # lastly, sort by total if there is a minimum event number and average is not forced, otherwise sort by average
    return sorted(avg_points, reverse=True, key=lambda k: k[2] if not min_events or sort_avg else k[1])

def main(year, min_events):
    results = parser.get(year)
    firstthree = pax.fastest(results, year)
    write_results(firstthree, year, min_events)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("year", type=int, default=datetime.now().year,
                        help="Year to read results, defaults to current year")
    # 11 events before drops
    argparser.add_argument("--drops", '-d', type=int, default=11, help="Number of minimum events before drops")
    args = argparser.parse_args()
    main(args.year, args.drops)
