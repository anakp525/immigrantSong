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

def empty(row):
	for i in row:
		if len(i) != 0:
			return False
	return True
	pass

def isHeader(row):
	if len(row[0]) == 0:
		return False
	for i in range(1,len(row)):
		if len(row[i]) != 0:
			return False
	return True

def grabYear(row):
	str = ""
	for r in row:
		str += r
		str += " "
	year = re.findall(r'\d\d\d\d', str)
	return year[0]

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
	#for block in blocks:
	#	print block
	return blocks

def convert(row, f, t):
	for i in range(len(row)):
		if row[i] == f:
			row[i] = t
	return row

def lastWord(row):
	words = re.split(':', row)
	return words[1]

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
		"""for row in reader:
			if ind == 0:
				year = grabYear(row)
				if year not in DHS:
					DHS[year] = {}
			elif ind == 1:
				type = grabType(row)
				if type not in DHS[year]:
					DHS[year][type] = {}

			if not empty(row):
				row = convert(row, '-','0.0')
				#for i in range(len(row)):
				#	if row[i] == "-":
				#		row[i] = "0.0"
				if row[0] == "Characteristic":
					continue
				data.append(row)
			ind += 1
		"""
	pass

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
