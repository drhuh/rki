#!/usr/bin/python3

# Datenquellen
# https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0/data?page=10
# https://www.arcgis.com/home/item.html?id=f10774f1c63e40168479a1feb6c7ca74

# Legende außerhalb: siehe https://pythonspot.com/matplotlib-legend/

import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from collections import defaultdict
from functools import partial
import datetime
from time import process_time

def rec_dd(depth=0):
    if depth == 2:
        return 0
    return defaultdict(partial(rec_dd, depth + 1))

parser = argparse.ArgumentParser(description='Analyze tasks in time sheet.')
parser.add_argument("-i", "--inputfile", required=True, type=str, help='name of time sheet file')

args = vars(parser.parse_args())
reportfile = args["inputfile"]

t1_start = process_time()

i = 0
tage = []
#countries = defaultdict(lambda : defaultdict(dict))
#countries = AutoVivification()
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

label_handles = {}
for country in countries:
    nof_rows = len(countries[country])
    # print(country, len(countries[country]), countries[country])
    tage = []
    infects = []
    last_sum = 0
    for key in sorted(countries[country]):
        # print(key, countries[country][key])
        tage.append(datetime.datetime.strptime(key, '%Y/%m/%d %H:%M:%S'))
        last_sum += countries[country][key]
        infects.append(last_sum)
    # print(country, last_sum)
    # x = np.linspace(1, nof_rows, nof_rows)
    y = np.array(infects)
    #plt.scatter(tage, y, label=country)
    handle, = plt.plot(tage, y, label=country)
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
print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)

plt.show()

