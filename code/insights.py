import sys
import os
from os.path import join
import re
import csv
import numpy
import matplotlib.pyplot as plt
import matplotlib
import json

# Plot a graph of the trend of US immigration over time from 2003-2011
def perYear(DHS):
	totals = {}
	years = []
	people = []
	for year in DHS:
		years.append(year)
		totals[year] = {'year':year,
		'm':DHS[year]['Country of Birth']['totals']['m'],
		'f':DHS[year]['Country of Birth']['totals']['f'],
		'u':DHS[year]['Country of Birth']['totals']['u']
    }
    		print year, totals[year]
	years.sort()
	for year in years:
		people.append(totals[year]['m']+totals[year]['f']+totals[year]['u'])
		print people[len(people)-1]
    
	plt.title("Immigration to US Over Time")
	plt.ylabel("Number of immigrants")
	plt.xlabel("Year")
	plt.xticks([2003,2004,2005,2006,2007,2008,2009,2010])
	plt.plot(years,people)
	plt.show()

	with open('immigration per year.csv', 'wb') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(years)
		writer.writerow(people)

# Order the dictionary from the json file by each state.
def getStates(info):
	states = {}
	for year in info:
		for state in info[year]['State of Residence']:
			if state == 'totals':
				continue
			if state not in states:
				states[state] = {'total':0}
			print state
			states[state][year] = info[year]['State of Residence'][state]['total']['m'] + info[year]['State of Residence'][state]['total']['f'] + info[year]['State of Residence'][state]['total']['u']
			states[state]['total'] += states[state][year]
	
	return states

def main():
    # Read file
    file = open('data.json', 'r')
    line = file.readline()
    file.close()

    DHS = json.loads(line)

    print DHS['2003']['State of Residence'][' Texas']

    perYear(DHS);
    stateInfo = getStates(DHS)	# Determine immigration by states
    print stateInfo
        
    # Order states by the total number of people
    sor = [(k, stateInfo[k]['total']) for k in stateInfo]
    l = sorted(sor, key=lambda x:x[1])
        
    for k in l:
        print k

if __name__ == "__main__":
    main()
