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
import datetime

parser = argparse.ArgumentParser(description='Analyze tasks in time sheet.')
parser.add_argument("-i", "--inputfile", required=True, type=str, help='name of time sheet file')

args = vars(parser.parse_args())
reportfile = args["inputfile"]

i = 0
tage = []
#countries = defaultdict(lambda: "")
countries = {}
nof_rows = 0
with open(reportfile, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        i += 1
        if i == 1:
            continue
        country = row[2]
        cnt_infect = int(row[6])
        cnt_death = int(row[7])
        cnt_date = datetime.datetime.strptime(row[8], '%Y/%m/%d %H:%M:%S')
        # print(type(row[8]), type(cnt_date))
        # print(country, cnt_infect, cnt_death, cnt_date)
        if country not in countries:
            countries[country] = {}
        if not cnt_date in countries[country]:
            countries[country][cnt_date] = cnt_infect
        else:
            countries[country][cnt_date] += cnt_infect

for country in countries:
    nof_rows = len(countries[country])
    # print(country, len(countries[country]), countries[country])
    tage = []
    infects = []
    last_sum = 0
    for key in sorted(countries[country]):
        # print(key, countries[country][key])
        tage.append(key)
        last_sum += countries[country][key]
        infects.append(last_sum)
    #print(countries[country])
    # x = np.linspace(1, nof_rows, nof_rows)
    y = np.array(infects)
    #plt.scatter(tage, y, label=country)
    plt.plot(tage, y, label=country)

plt.legend()
plt.show()
