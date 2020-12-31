#!/usr/bin/python3

# Legende außerhalb: siehe https://pythonspot.com/matplotlib-legend/

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

parser = argparse.ArgumentParser(description='Analyze tasks in time sheet.')
parser.add_argument("-i", "--inputfile", required=True, type=str, help='name of time sheet file')

args = vars(parser.parse_args())
reportfile = args["inputfile"]

rki_sheets = pd.read_excel(reportfile, engine="openpyxl", sheet_name='BL_7-Tage-Fallzahlen', header=None)
contents = rki_sheets.to_dict(orient='record')
i = 0
tage = []
countries = {}
nof_rows = 0
for row in contents:
    i += 1
    if i == 1:
        continue
    if i == 2:
        print(row[0])
        continue
    if i == 3:
        nof_rows = len(row)
        for j in range(1, nof_rows):
            tage.append(row[j])
        # print(tage)
        continue
    country = row[0]
    fallzahlen = []
    nof_rows = len(row)
    last_value = 0
    for j in range(1, nof_rows):
        if type(row[j]) != pd._libs.tslibs.nattype.NaTType:
            last_value = last_value + row[j]/7
            fallzahlen.append(last_value)
    countries[country] = fallzahlen
    # print(countries[country])


for country in countries:
    if country == 'Gesamt':
        continue
    nof_rows = len(countries[country])
    days_to_plot = tage[0:nof_rows]
    #print(nof_rows, len(countries[country]))
    #print(countries[country])
    # x = np.linspace(1, nof_rows, nof_rows)
    y = np.array(countries[country])
    plt.plot(days_to_plot, y, label=country)

plt.legend()
plt.show()