#!/usr/bin/env python3

# prerequisites: see requirements.txt
# sudo pip3 install -r requirements.txt

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

# from pandas.plotting import register_matplotlib_converters
# register_matplotlib_converters()

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
MY_DPI = 100
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
parser.add_argument("-m", "--mortality", required=False, action='store_true', help='mortality instead of infections')
parser.add_argument("-p", "--percentage", required=False, type=str,
                    help='plot percentage values based on provided file')
parser.add_argument("-s", "--saveplot", required=False, type=str, help='save figure in png file instead')

args = vars(parser.parse_args())
plotdelta = args["delta"]
fetchnewdata = args["fetch"]
geometry = args["geometry"]
reportfile = args["inputfile"]
mortalitiy = args["mortality"]
percentagefile = args["percentage"]
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


if mortalitiy:
    description = "Sterbefälle"
else:
    description = "Infektionen"


if fetchnewdata:
    download(DATA_URL, reportfile)

title_format = "{:d}"
inhabitants = {}
if percentagefile:
    title_format = "{:f}"
    with open(percentagefile, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            inhabitants[row[0]] = int(row[1])
            # print("Bundesland: {:s} Einwohner: {:d}".format(row[0], inhabitants[row[0]]))


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
        if mortalitiy:
            cnt_infect = int(row[7])
        else:
            cnt_infect = int(row[6])
        # cnt_date = datetime.datetime.strptime(row[8], '%Y/%m/%d %H:%M:%S')
        cnt_date = row[8]
        # print(type(row[8]), type(cnt_date))
        # print(country, cnt_infect, cnt_death, cnt_date)
        countries[country][cnt_date] += cnt_infect

t1_read = process_time()
print("Elapsed time for reading csv file in seconds: {:.2f}".format(t1_read - t1_start))

fig = plt.figure(figsize=(X_GEOMETRY/MY_DPI, Y_GEOMETRY/MY_DPI), dpi=MY_DPI)
label_handles = {}
# lotsa_colors = list(colors.get_named_colors_mapping().values())
# lotsa_colors = list(mcd.XKCD_COLORS.values())
# print(lotsa_colors)
my_color_list = ('lightcoral', 'red', 'peru', 'darkorange', 'gold', 'olivedrab', 'greenyellow', 'forestgreen',
                 'teal', 'cyan', 'dodgerblue', 'blue', 'darkviolet', 'magenta', 'mediumvioletred', 'crimson')
i = -1
label_sum = 0
for country in countries:
    i += 1
    nof_rows = len(countries[country])
    # print(country, len(countries[country]), countries[country])
    tage = []
    infects = []
    delta = []
    last_sum = 0
    total_sum = 0
    last_key_value = 0
    for key in sorted(countries[country]):
        # print(key, countries[country][key])
        tage.append(datetime.datetime.strptime(key, '%Y/%m/%d %H:%M:%S'))
        currval = countries[country][key]
        last_key_value = currval
        total_sum += currval
        if percentagefile:
            currval = currval / inhabitants[country] * 100  # in percent
        last_sum += currval

        if plotdelta:
            delta.append(currval)
        else:
            infects.append(last_sum)

    # print(country, last_sum)
    # x = np.linspace(1, nof_rows, nof_rows)
    if plotdelta:
        y = np.array(delta)
        last_value = delta[-1]
    else:
        y = np.array(infects)
        last_value = last_sum

    if percentagefile:
        if plotdelta:
            handle, = plt.plot(tage, y,
                               label="{:s} ({:.3f} % ({:d} / {:d}))".
                               format(country, last_value, last_key_value, inhabitants[country]),
                               color=my_color_list[i])
        else:
            handle, = plt.plot(tage, y,
                               label="{:s} ({:.2f} % ({:d} / {:d}))".
                               format(country, last_value, total_sum, inhabitants[ country]),
                               color=my_color_list[i])
    else:
        handle, = plt.plot(tage, y, label="{:s} ({:d})".format(country, last_value), color=my_color_list[i])

    # plt.scatter(tage, y, label=country)
    label_handles[handle] = last_value
    label_sum += last_value

# print(label_handles)
sorted_handles = sorted(label_handles.items(), key=lambda x: x[1], reverse=True)
# print(sorted_handles)
handles = []
if percentagefile:
    if plotdelta:
        leghandle = plt.plot([], [], ' ', label="Legende: Bundesland (Fälle in % ({:s} pro Tag / Einwohner))".
                             format(description))
    else:
        leghandle = plt.plot([], [], ' ', label="Legende: Bundesland (Fälle in % ({:s} gesamt / Einwohner))".
                             format(description))
else:
    leghandle = plt.plot([], [], ' ', label="Legende: Bundesland (Anzahl der {:s})".format(description))
handles.append(leghandle[0])

for handle in sorted_handles:
    handles.append(handle[0])
# print(handles)
plt.legend(handles=handles)

if plotdelta:
    if percentagefile:
        titlestring = "{:s} pro Tag bezogen auf die Einwohner des Bundeslandes (in %) bis zum {:s}".\
            format(description,tage[-1].date().strftime("%d %b %Y"))
    else:
        titlestring = "{:s} pro Tag je Bundesland bis zum {:s}, Summe = {:d} (letzer Tag)".\
            format(description,tage[-1].date().strftime("%d %b %Y"),label_sum)
else:
    if percentagefile:
        titlestring = "{:s} bezogen auf die Einwohner des Bundeslandes (in %) bis zum {:s}".\
            format(description,tage[-1].date().strftime("%d %b %Y"))
    else:
        titlestring = "{:s} je Bundesland bis zum {:s}, Summe = {:d}".\
            format(description,tage[-1].date().strftime("%d %b %Y"),label_sum)

plt.title(titlestring)
plt.xlabel("Datum")
if percentagefile:
    plt.ylabel("{:s} bezogenauf die Einwohner pro Bundesland (in %)".format(description))
else:
    plt.ylabel("Anzahl der {:s}".format(description))

t1_stop = process_time()
print("Elapsed time during the whole program in seconds: {:.2f}".format(t1_stop - t1_start))

if saveplot:
    plt.savefig(saveplot)
else:
    plt.show()
