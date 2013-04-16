import sys
import json
import os

def createBy(data, how):
	fileName = how + '.csv'
	# Get headings
	headings = ['year', 'collectionType', ']
	with open(fileName, 'wb') as file:
		writer = csv.writer(file)
		for state in data:
		
	file.close()
	pass

def mergeAll():
	pass

def createCSVFiles(data):
	createBy(data, 'state of residence')
	createBy(data, 'msa')
	createBy(data, 'cbsa')
	createBy(data, 'country of birth')
	mergeAll()
	
def main():
	file = open('data.json', 'r')
	line = file.readline()
	file.close()
	DHS = json.loads(line)	
	
	createCSVFiles(DHS)
	print DHS

main()
