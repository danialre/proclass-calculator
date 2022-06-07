### parser.py
import os
import pandas
from urllib.error import HTTPError

MAX_EVENTS = 35
BASE_URL = "https://<your club website here>/images/results/{year}/pe{event}_fin.htm"
BASE_FILE = "{year}/pe{event}.csv"
CONSECUTIVE_CACHE = 10

def collect_events(year, force_update=False):
    # collect event results from the website or from local files
    if not os.path.exists(str(year)):
        os.mkdir(str(year))
    results = []
    cache_counter = 0
    for pe in range(1, MAX_EVENTS + 1):
        if force_update or not os.path.exists(BASE_FILE.format(year=year, event=pe)):
            if cache_counter > CONSECUTIVE_CACHE and not force_update:
                print(f'Guessing {pe - 1} events exist, not checking website')
                break # a bunch of cached files in a row, there probably isn't a new event we're missing
            else:
                cache_counter = 0 # reset counter

            # get table from the website if we don't have a local copy
            print(f'Accessing {BASE_URL.format(year=year, event=pe)}')
            try:
                tables = pandas.read_html(BASE_URL.format(year=year, event=pe))
            except HTTPError as e:
                print('Warning: HTTP error encountered')
                break # stop loop, no more events

            # figure out which table has all the data - more than 20 rows (10 drivers) is good
            for table in tables:
                if len(table) > 20:
                    if 'Class' not in table.columns:
                        # alternate format detected
                        table = pandas.read_html(BASE_URL.format(year=year, event=pe), header=None)
                        # classes have their own headings so make a new header
                        new_header = ['Pos', 'Class', '#', 'Driver', 'Car', 'Color', 'Run 1..', 'Run 2..', 'Run 3..']
                        # fill the rest of the column names with blanks
                        new_header += ['R'] * (len(table.columns) - len(new_header))
                        table.columns = new_header
                    results.append(table)
                    # also save for later
                    table.to_csv(f"{year}/pe{pe}.csv", index=False)
                    continue
        else:
            # otherwise read the saved csv of results
            table = pandas.read_csv(BASE_FILE.format(year=year, event=pe))
            if 'Class' not in table.columns:
                # alternate format detected
                table = pandas.read_csv(BASE_FILE.format(year=year, event=pe), header=None)
                # classes have their own headings so make a new header
                new_header = ['Pos', 'Class', '#', 'Driver', 'Car', 'Color', 'Run 1..', 'Run 2..', 'Run 3..']
                # fill the rest of the column names with blanks
                new_header += ['R'] * (len(table.columns) - len(new_header))
                table.columns = new_header
            results.append(table)
            cache_counter += 1

    # make sure results are formatted properly
    for idx in range(len(results)):
        if 'Class' not in results[idx].columns:
            results[idx].columns = results[idx].iloc[0]
            results[idx] = results[idx][1:].reset_index()

    return results

def filter_tables(results):
    # filter tables for first three runs and exclude blank rows
    filtered = []
    for result in results:
        # dropna - drop excess run rows and only get first three runs
        try:
            filtered.append(result.dropna(subset=['Class'])[["Class", "#", "Driver", "Run 1..", "Run 2..", "Run 3.."]])
        except KeyError:
            # alternate format detected, drop additional class headers
            result = result.dropna(subset=['Class'])
            result = result[result['Class'].str.contains('Total Entries') == False]
            filtered.append(result.dropna(subset=['Class'])[["Class", "#", "Driver", "Run 1..", "Run 2..", "Run 3.."]])
    return filtered

def get(year, force_update=False):
    # get a filtered list of event tables
    return filter_tables(collect_events(year, force_update))
