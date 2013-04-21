import sys
import json
import os
import csv
import re

def writeCSV(info, fileName):
	with open(fileName, 'wb') as file:
		writer = csv.writer(file)
		for row in sorted(info, key = lambda x:x[0]):
			line = []
			for value in row:
				line.append(value)
			writer.writerow(line)
		file.close()

def getTotal(row):
	total = 0.0
	m = row['m']
	f = row['f']
	u = row['u']
	return m+f+u

def dataByState(data, type = 'State of Residence'):
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
					#if value not in d[region][year][cat]:
					#	d[region][year][cat][value] = {}
					total = getTotal(data[year][type][region][cat][value])
					numberImmigrants = numberImmigrants + total
					if total > topValue[1]:
						topValue = (str(value), total)
					"""for gender in data[year][type][region][cat][value]:
						if gender not in d[region][year][cat][value]:
							d[region][year][cat][value][gender] = data[year][type][region][cat][value][gender]
					
					m = data[year][type][region][cat][value]['m']
					f = data[year][type][region][cat][value]['f']
					u = data[year][type][region][cat][value]['u']
					"""
				d[region][year][cat][topValue[0]] = topValue[1]
				#print numberImmigrants
				if numberImmigrants == 0:
					US.append( (region, year, cat, topValue, 100.0) )
				else:
					US.append( (region, year, cat, topValue, float(topValue[1]/numberImmigrants)*100) )
				#US.append( (region, year, cat, value, topValue, total""", {'u':u, 'f':f, 'm':m}""") )
	
	#for key in sorted(US, key=lambda x:x[0]):
	#	print key
	return d #US 

def convertToDict(l):
	rows = []
	states = {}
	for item in l:	# 5 tuple - region, year, category, (top Category, value), percentage
		row = ()
		state = item[0]
		year = item[1]
		immigrants = 0.0
		maleImmigrants = 0.0
		femaleImmigrants = 0.0
		topCategory = ''
		topValue = ''
		if state not in states:
			states[state] = {}
		if year not in states[state]:
			states[state][year] = {}
	
		category = item[2]
		if category == 'Number of immigrants:':
			immigrants = item[3]['m'] + item[3]['f'] + item[3]['u']
			maleImmigrants = item[3]['m']
			femaleImmigrants = item[3]['f']
			if category not in states[state][year]:
				states[state][year][category] = {}
			states[state][year][category]['m'] = item[3]['m']
			states[state][year][category]['f'] = item[3]['f']
			states[state][year][category]['total'] = immigrants
		else:
			topCategory = item[3][0]
			topValue = item[3][1]
			if category not in states[state][year]:
				states[state][year][category] = {}
			if topCategory not in states[state][year][category]:
				states[state][year][category][topCategory] = topValue
		row = (state, year, immigrants, maleImmigrants, femaleImmigrants, category, topCategory, topValue) 
		rows.append(row)

	sortedRows = sorted(rows, key=lambda x:x[0])
	actual = []
	#concatenate Rows
	for i in range(len(sortedRows)):
		row = sortedRows[i]
		state = row[0]
		if sortedRows[i+1][0] == state:	# Same state. Concatenate values
			pass	
		else:				# Last state
			pass
			
		#print row
	#for k in states:
	#	print k, states[k]
	return states
	pass

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

def main():
	file = open('data.json', 'r')
	line = file.readline()
	file.close()
	DHS = json.loads(line)	

	byState = dataByState(DHS)
	states = createRows(byState)
	statesapriori = createRows(byState, False)
	writeCSV(states, 'US.csv')
	writeCSV(statesapriori, 'USapriori.csv')

	byCountry = dataByState(DHS, 'Country of Birth')
	countries = createRows(byCountry)
	countriesapriori = createRows(byCountry, False)
	writeCSV(countries, 'world.csv')
	writeCSV(countriesapriori, 'worldapriori.csv')


main()
