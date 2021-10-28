#!/usr/bin/python3

# prerequisites
# sudo pip3 install pandas
# sudo pip3 install tqdm
# if using colors from matplotlib
#   sudo pip3 install matplotlib

# Datenquellen
# https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0/data?page=10
# https://www.arcgis.com/home/item.html?id=f10774f1c63e40168479a1feb6c7ca74
#
# Die Daten selbst kann man direkt mit
#
# wget https://www.arcgis.com/sharing/rest/content/items/f10774f1c63e40168479a1feb6c7ca74/data
#
# herunterladen

# Legende außerhalb: siehe https://pythonspot.com/matplotlib-legend/
# Download siehe https://stackoverflow.com/questions/15644964/python-progress-bar-and-downloads

import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
from collections import defaultdict
from functools import partial
import datetime
import requests
from time import process_time
from tqdm import tqdm
# import matplotlib.colors as colors
# import matplotlib._color_data as mcd

DATA_URL = "https://www.arcgis.com/sharing/rest/content/items/f10774f1c63e40168479a1feb6c7ca74/data"
MEAN_DAYS = 7
MY_DPI=100
DEFAULT_X_GEOMETRY = 1024
DEFAULT_Y_GEOMETRY = 768

def rec_dd(depth=0):
    if depth == 2:
        return 0
    return defaultdict(partial(rec_dd, depth + 1))


def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w


def download(url: str, fname: str):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


parser = argparse.ArgumentParser(description='Analyze tasks in time sheet.')
parser.add_argument("-d", "--delta", required=False, action='store_true', help='plot delta instead of absolute numbers')
parser.add_argument("-f", "--fetch", required=False, action='store_true',
                    help='fetch new data set and store it in file name defined by -i option')
parser.add_argument("-g", "--geometry", required=False, type=str,
                    help='geometry of saved picture, default %dx%d'.format(DEFAULT_X_GEOMETRY, DEFAULT_Y_GEOMETRY))
parser.add_argument("-i", "--inputfile", required=True, type=str, help='name of time sheet file')
parser.add_argument("-r", "--relative", required=False, action='store_true', help='plot delta relative')
parser.add_argument("-s", "--saveplot", required=False, action='store_true', help='save figure in .png file instead')

args = vars(parser.parse_args())
plotdelta = args["delta"]
fetchnewdata = args["fetch"]
geometry = args["geometry"]
reportfile = args["inputfile"]
plotrelative = args["relative"]
saveplot = args["saveplot"]

if geometry:
    if geometry.count('x') != 1:
        print('geometry must have the format VALUExVALUE, e.g. 1024x768')
        exit(-1)
    geomvals=geometry.split("x")
    X_GEOMETRY=int(geomvals[0])
    Y_GEOMETRY=int(geomvals[1])
else:
    X_GEOMETRY=DEFAULT_X_GEOMETRY
    Y_GEOMETRY=DEFAULT_Y_GEOMETRY


if fetchnewdata:
    download(DATA_URL, reportfile)

t1_start = process_time()

i = 0
tage = []
# countries = defaultdict(lambda : defaultdict(dict))
# countries = AutoVivification()
countries = rec_dd()
nof_rows = 0
with open(reportfile, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        i += 1
        if i == 1:
            continue
        country = row[2]
        cnt_infect = int(row[6])
        # cnt_death = int(row[7])
        # cnt_date = datetime.datetime.strptime(row[8], '%Y/%m/%d %H:%M:%S')
        cnt_date = row[8]
        # print(type(row[8]), type(cnt_date))
        # print(country, cnt_infect, cnt_death, cnt_date)
        countries[country][cnt_date] += cnt_infect

t1_read = process_time()
print("Elapsed time for reading csv file in seconds:", t1_read - t1_start)

fig = plt.figure(figsize=(X_GEOMETRY/MY_DPI, Y_GEOMETRY/MY_DPI), dpi=MY_DPI)
label_handles = {}
# lotsa_colors = list(colors.get_named_colors_mapping().values())
# lotsa_colors = list(mcd.XKCD_COLORS.values())
# print(lotsa_colors)
my_color_list = ('lightcoral', 'red', 'peru', 'darkorange', 'gold', 'olivedrab', 'greenyellow', 'forestgreen',
                 'teal', 'cyan', 'dodgerblue', 'blue', 'darkviolet', 'magenta', 'mediumvioletred', 'crimson')
i = -1
for country in countries:
    i += 1
    nof_rows = len(countries[country])
    # print(country, len(countries[country]), countries[country])
    tage = []
    infects = []
    delta = []
    last_sum = 0
    for key in sorted(countries[country]):
        # print(key, countries[country][key])
        tage.append(datetime.datetime.strptime(key, '%Y/%m/%d %H:%M:%S'))
        last_sum += countries[country][key]
        infects.append(last_sum)
        if plotdelta:
            delta.append(countries[country][key])
    # print(country, last_sum)
    # x = np.linspace(1, nof_rows, nof_rows)
    if plotdelta:
        if plotrelative:
            delta[:] = [x / last_sum for x in delta]
        y = np.array(moving_average(delta, MEAN_DAYS))
        # handle, = plt.plot(tage[MEAN_DAYS-1:], y, label=country, color='#204080')
        handle, = plt.plot(tage[MEAN_DAYS - 1:], y, label=country, color=my_color_list[i])
    else:
        y = np.array(infects)
        handle, = plt.plot(tage, y, label="{:s} ({:d})".format(country, last_sum), color=my_color_list[i])
    # plt.scatter(tage, y, label=country)
    label_handles[handle] = last_sum

# print(label_handles)
sorted_handles = sorted(label_handles.items(), key=lambda x: x[1], reverse=True)
# print(sorted_handles)
handles = []
for handle in sorted_handles:
    handles.append(handle[0])
# print(handles)
plt.legend(handles=handles)

t1_stop = process_time()
print("Elapsed time during the whole program in seconds:", t1_stop - t1_start)

if saveplot:
    plt.savefig('save.png')
else:
    plt.show()
