import sys
import os
from os.path import join
import re
import csv
import numpy
import matplotlib.pyplot as plt
import matplotlib
import json

data = []
DHS = {}

# Goal is to read all the Department of Homeland Security data and write it to a 
# json file. Because the data was ill-formatted and contained many sections of 
# information per file, I grab each block of data and determine what to do
# with it.

# Determine if a row of data is empty. This is the seperator between blocks.
def empty(row):
	for i in row:
		if len(i) != 0:
			return False
	return True
	pass

# Determine if the row is a header. Contains only one data element, and comes immediately
# after an empty row.
def isHeader(row):
	if len(row[0]) == 0:
		return False
	for i in range(1,len(row)):
		if len(row[i]) != 0:
			return False
	return True

# Get the important year from the row. I know that the row is always in a 4-digit year format.
def grabYear(row):
	str = ""
	for r in row:
		str += r
		str += " "
	year = re.findall(r'\d\d\d\d', str)
	return year[0]

# The type of the information can only be one of four - {MSA, CBSA, Region/Country of Birth, State of Residence}
def grabType(row):
	str = ""
	for r in row:
		str += r
		str += " "
	if re.search('MSA', str) != None:
		return "MSA"
	if re.search('CBSA', str) != None:
		return "CBSA"
	if re.search('Region/Country of Birth', str) != None:
		return "Country of Birth"
	if re.search('State of Residence', str) != None:
		return "State of Residence"

	
	return "?"

# This code section will actually grab all the blocks from a given file in our set.
# It will return the sections pertaining to Age, Marital Status, Top Countries/States,
# and occupation.
def getBlocks(rows):
	blocks = []
	block = []
	for row in rows:
		if isHeader(row) == True:
			if len(block) != 0:
				blocks.append(block)
			block = []
			block.append(row)
		elif not empty(row):
			block.append(row)
	
	return blocks

# Convert a particular element in a row from value 1 to value 2.
# May be using to remove spaces, hyphens, etc (instead of using re)
def convert(row, f, t):
	for i in range(len(row)):
		if row[i] == f:
			row[i] = t
	return row

# Returns the end of a line (i.e. value: end)
def lastWord(row):
	words = re.split(':', row)
	return words[1]

# Actually read the file, grab the blocks, and put in a dictionary
# to put in the json file.
def readFile(file):
	with open(file) as infile:
		reader = csv.reader(infile)

		ind = 0
		# First row - get year
		year = -1
		type = ""
		
		blocks = getBlocks(reader)
		year = grabYear(blocks[0][0])
		if year not in DHS:
			DHS[year] = {}
		type = grabType(blocks[1][0])
		if type not in DHS[year]:
			DHS[year][type] = {}

		state = lastWord(blocks[2][0][0])
		blocks[2][2] = convert(blocks[2][2], 'D', 0.0)
		blocks[2][2] = convert(blocks[2][2], '-', 0.0)
		
		if state not in DHS[year][type]:
			DHS[year][type][state] = {'total':{}}
		DHS[year][type][state]['total']['m'] = float(blocks[2][2][2])
		DHS[year][type][state]['total']['f'] = float(blocks[2][2][3])
		DHS[year][type][state]['total']['u'] = float(blocks[2][2][4])

		if 'totals' not in DHS[year][type]:
			DHS[year][type]['totals'] = {}
			DHS[year][type]['totals']['m'] = float(blocks[2][2][2])
			DHS[year][type]['totals']['f'] = float(blocks[2][2][3])
			DHS[year][type]['totals']['u'] = float(blocks[2][2][4])
		else:
			DHS[year][type]['totals']['m'] += float(blocks[2][2][2])
			DHS[year][type]['totals']['f'] += float(blocks[2][2][3])
			DHS[year][type]['totals']['u'] += float(blocks[2][2][4])

		# Loop through remaining blocks
		for i in range(3,len(blocks)-2):
			block = blocks[i]
			head = block[0][0]
			if head not in DHS[year][type][state]:
				DHS[year][type][state][head] = {}
			for j in range(1, len(block)):
				t = block[j][0]

				try:
					m = float(block[j][2])
				except:
					m = 0.0
				try:
					f = float(block[j][3])
				except:	
					f = 0.0
				try:
					u = float(block[j][4])
				except:
					u = 0.0
				
				if t not in DHS[year][type][state][head]:
					DHS[year][type][state][head][t] = {}
					DHS[year][type][state][head][t]['m'] = m
					DHS[year][type][state][head][t]['f'] = f
					DHS[year][type][state][head][t]['u'] = u
				else:
					DHS[year][type][state][head][t]['m'] += m
					DHS[year][type][state][head][t]['f'] += f
					DHS[year][type][state][head][t]['u'] += u
	pass

# Do some preliminary statistics on the number of immigrants to the US over time.
# Create a plot using matplotlib
def perYear():
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
	years.sort()
	for year in years:
		people.append(totals[year]['m']+totals[year]['f']+totals[year]['u'])
		print people[len(people)-1]
		
	plt.title("Immigration to US Over Time")
	plt.ylabel("Number of immigrants")
	plt.xlabel("Year")
	plt.xticks([2003,2004,2005,2006,2007,2008,2009,2010])
	print years
	print people
	plt.plot(years,people)
	plt.show()
	
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
	for root, dirs, files in os.walk('DATA'):
		#print "Current directory", root
		#print "Sub directories", dirs
		for file in files:
			if file.endswith('.csv'):
				if re.search('ook2.csv',file) == None:
					readFile(os.path.join(root, file))

    	perYear()			# Find the number of immigrants per year for US
	print DHS['2003']['State of Residence'][' Texas']
	stateInfo = getStates(DHS)	# Determine immigration by states
	print stateInfo

	# Order states by the total number of people
	sor = [(k, stateInfo[k]['total']) for k in stateInfo]
	l = sorted(sor, key=lambda x:x[1])

	for k in l:
		print k

	# Write dictionary to a file
	file = open('data.json','w')
	file.write(json.dumps(DHS))
	file.close()
	"""for year in DHS:
		print year
		for category in DHS[year]:
			for a in range(100):
				print
			print '\t', category
			for state in DHS[year][category]:
				print '\t\t', state
				for label in DHS[year][category][state]:
					print '\t\t\t', label
					print '\t\t\t', DHS[year][category][state][label]
"""

if __name__ == "__main__":
	main()
