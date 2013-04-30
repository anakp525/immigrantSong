import sys
import json
import os
import csv
import re

# Generic function to write a CSV file from a list of items
def writeCSV(info, fileName):
	with open(fileName, 'wb') as file:
		writer = csv.writer(file)
		for row in sorted(info, key = lambda x:x[0]):
			line = []
			for value in row:
				line.append(value)
			writer.writerow(line)
		file.close()

# Get the total of every category (male+female+unknown)
def getTotal(row):
	total = 0.0
	m = row['m']
	f = row['f']
	u = row['u']
	return m+f+u


# Grab all the data by a particular state. Only include information for the top category
# of that state. If Proffessional is the leading occupation, only include professional for
# that state.
def dataByState(data, type = 'State of Residence', top = True):
	d = {}
	US = []
	numberImmigrants = 0
	for year in data:
		year = str(year)
		for region in data[year][type]:
			region = str(region)
			if region == 'totals':
				continue
			if region not in d:
				d[region] = {}
			d[region][year] = {}
			for cat in data[year][type][region]:
				if region == ' Albania' and year == '2003':
					print cat
				cat = str(cat)
				if cat == 'total':
					m = data[year][type][region][cat]['m']
					f = data[year][type][region][cat]['f']
					u = data[year][type][region][cat]['u']
					d[region][year]['number of immigrants'] = m+f+u
					d[region][year]['number female'] = f
					d[region][year]['number male'] = m
					US.append( (region, year, 'Number of immigrants:', {'u':u, 'f':f, 'm':m}) )
					continue
				if cat not in d[region][year]:
					d[region][year][cat] = {}
				topValue = ('blah', -100)
				numberImmigrants = 0
				for value in data[year][type][region][cat]:
					value = str(value)
					if value == 'Unknown' or value == 'Other' or value == "No occupation" or value == "No occupation/not working outside home":
						continue
					total = getTotal(data[year][type][region][cat][value])
					numberImmigrants = numberImmigrants + total
					if top == True:
						if total > topValue[1]:
							topValue = (str(value), total)
					else:
						d[region][year][cat][value] = total
				if top == True:
					d[region][year][cat][topValue[0]] = topValue[1]
				
				if numberImmigrants == 0:
					US.append( (region, year, cat, topValue, 100.0) )
				else:
					US.append( (region, year, cat, topValue, float(topValue[1]/numberImmigrants)*100) )
	
	return d #US 

# Function to create all the rows [in list format] that will get written to the CSV file.
# I specify whether the data needs to be written to feed into the visualization or not.
# The format of the data varies depending on that.
def createRows(data, vis = True):
	rows = []
	cats = ['number of immigrants', 'Occupation', 'Leading states of permanent residence', 'Leading countries of birth', 'number male', 'number female']
	years = range(2003,2011)
	for state in data:
		state = str(state)
		row = []
		row.append(state)
		for year in years:
			year = str(year)
			if year not in data[state]:
				if vis == True:
					row.append(year)
				for cat in cats:
					if vis == True:
						row.append(cat)
						row.append('')
			else:
				if vis == True:
					row.append(year)
				else:
					row.append('year: '+ year)
				for cat in cats:
					if vis == True:
						row.append(cat)
					if cat not in data[state][year]:
						if vis == True:
							row.append('')
						else:
							row.append(cat + ': ?')
						continue
					if cat == 'Age' or cat == 'Marital status':
						continue
					if cat == 'Occupation' or cat == "Leading states of permanent residence" or cat == "Leading countries of birth":
						for k in data[state][year][cat]:
							if vis == True:
								row.append(k)
							else:
								row.append(cat+ ': ' + str(k))
					else:
						if vis == True:
							row.append(data[state][year][cat])
						else:
							row.append(cat + ': '+ str(data[state][year][cat]))
			if vis == False:
				if len(row) > 1:
					rows.append(row)
				row = []
				row.append(state)
		if vis == True:
			rows.append(row)
	#for r in rows:
	#	print r

	return rows

# Destroy all commas and replace them with a slash. The rows will be in a CSV so there
# should not be any commas in each heading title or value for a row
def killCommas(row):
	return re.sub(r',', '/', row)
		
# Create the csv file format for the apriori input on the country.
def createCountryApriori(data):
	years = range(2003,2011)
	cats = ['number of immigrants', 'number male', 'number female']
	cats2 = ['Occupation', 'Leading states of permanent residence', 'Age', 'Marital Status']
	
	rows = []
	for state in data:
		state = str(state)
		for year in years:
			year = str(year)
			row = []
			if year in data[state]:
				row.append(str(state))
				row.append(str(year))
				for cat in cats:
					if cat in data[state][year]:
						newRow = killCommas(str(data[state][year][cat]))
						row.append(cat + ': ' + newRow)
					else:
						row.append(cat + ': ?')
				for cat in cats2:
					if cat in data[state][year]:
						for k in data[state][year][cat]:
							k = killCommas(k)
							row.append(cat + ': ' + k)
					else:
						row.append(cat + ': ?')
				rows.append(row)
	return rows

# Create the csv file format for the input to the apriori algorithm for each state
def createStateApriori(data):
	years = range(2003,2011)
	cats = ['number of immigrants', 'number male', 'number female']
	cats2 = ['Occupation', 'Leading countries of birth', 'Age', 'Marital Status']
	
	rows = []
	for state in data:
		state = str(state)
		for year in years:
			year = str(year)
			row = []
			if year in data[state]:
				row.append(str(state))
				row.append(str(year))
				for cat in cats:
					if cat in data[state][year]:
						newRow = killCommas(str(data[state][year][cat]))
						row.append(cat + ': ' + newRow)
					else:
						row.append(cat + ': ?')
				for cat in cats2:
					if cat in data[state][year]:
						for k in data[state][year][cat]:
							k = killCommas(k)
							row.append(cat + ': ' + k)
					else:
						row.append(cat + ': ?')
				rows.append(row)
	return rows

# Get all of the countries from a dictionary
def getCountries(data):
	l = [key for key in data]
	rows = []
	for country in sorted(l, key=lambda x:x[0]):
		rows.append([country])
	return rows

# Grab all the top countries from a dictionary
def getTopCountries(data):
	rows = []
	cs = []
	for state in data:
		for year in data[state]:
			row = []
			if 'Leading countries of birth' in data[state][year]:
				for c in data[state][year]['Leading countries of birth']:
					row.append(c)
					if [c] not in cs:
						cs.append([c])
				row.append(year)
				row.append(state)
				rows.append(row)
	print cs
	return rows, cs

# Make all the CSV files
def main():
	file = open('data.json', 'r')
	line = file.readline()
	file.close()
	DHS = json.loads(line)	
	print DHS

	byState = dataByState(DHS)
	states = createRows(byState)
	states2 = createRows(byState, False)
	print states2
	statesapriori = createStateApriori(byState)
	writeCSV(states, 'US.csv')
	writeCSV(statesapriori, 'USapriori.csv')
	writeCSV(states2, 'USapriori2.csv')
	
	byCountry = dataByState(DHS, 'Country of Birth')
	countries = createRows(byCountry)
	countriesapriori = createCountryApriori(byCountry)
	writeCSV(countries, 'world.csv')
	writeCSV(countriesapriori, 'worldapriori.csv')

	countries = getCountries(byCountry)
	writeCSV(countries, 'allcountries.csv')

	topCountries, unique = getTopCountries(byState)
	writeCSV(topCountries, 'topCountries.csv')
	writeCSV(list(unique), 'uniqueCountries.csv')
main()
