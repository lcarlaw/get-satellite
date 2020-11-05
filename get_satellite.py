"""
Usage:

    python get_satellite.py -s 2018-01-07/12 -e 2018-01-07/18 -c 13 -r southeast
    [Downloads the southeast regional view]

    or:

    python get_satellite.py -s 2018-01-07/12 -e 2018-01-07/18 -c 13
    [Defaults to north central]

"""

from __future__ import print_function
from datetime import datetime, timedelta
import argparse

try:
    from urllib.request import urlopen, URLError, urlretrieve       # Python 3
except ImportError:
    from urllib2 import urlopen, URLError                           # Python 2
    from urllib import urlretrieve

DOWNLOAD_DIR = '/Users/leecarlaw/satellite_data'

base = 'https://mtarchive.geol.iastate.edu'
tail = 'cod/sat/goes16/regional/'

def query_files(start, end, channel, region=None):

    if channel not in ['airmass', 'natcolor', 'ntmicro', 'truecolor']:
        channel = 'abi' + str(int(channel)).zfill(2)
    if not region: region = 'northcentral'

    # Determine the unique months, days, and years we need.
    start_dt = datetime.strptime(start, '%Y-%m-%d/%H')
    end_dt = datetime.strptime(end, '%Y-%m-%d/%H')
    years = set()
    months = set()
    days = set()
    start = start_dt
    while start <= end_dt:
        years.add(start.year)
        months.add(start.month)
        days.add(start.day)
        start += timedelta(hours=1)

    # Create the list of requested images
    files = []
    for year in list(years):
        for month in list(months):
            for day in list(days):
                URL = "%s/%s/%s/%s/%s/%s/%s" % (base, str(year).zfill(4), str(month).zfill(2),
                                                str(day).zfill(2), tail, region, channel)
                f_list = urlopen(URL + '/000index.txt')
                for f in f_list:
                    f = f.decode('utf-8')
                    idx = f.rindex('_') + 1
                    datestring = f[idx:idx+14]
                    dt = datetime.strptime(datestring, '%Y%m%d%H%M%S')
                    if start_dt <= dt <= end_dt:
                        # Remove the carriage return character and append to file list.
                        f = f.strip('\n')
                        files.append("%s/%s" % (URL, f))
    return files

def download_files(file_list):
    for f in file_list:
        fname_idx = f.rfind('/') + 1
        fname = f[fname_idx:]
        try:
            print(fname)
            urlretrieve(f, "%s/%s" % (DOWNLOAD_DIR, fname))
        except:
            pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', dest='start', help='YYYY-mm-dd/HH')
    ap.add_argument('-e', dest='end', help='YYYY-mm-dd/HH')
    ap.add_argument('-c', dest='channel', help='1,2,3,...16, airmass, natcolor, ntmicro, \
                                                truecolor')
    ap.add_argument('-r', dest='region', help='[OPTIONAL] gulf, northcentral, northeast, \
                                               northmexico, northwest, prregional, \
                                               southcentral, southeast, southmexico, \
                                               southwest')
    args = ap.parse_args()
    file_list = query_files(args.start, args.end, args.channel, region=args.region)
    download_files(file_list)

if __name__ == '__main__': main()
