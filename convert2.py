import sys
import os
from os.path import join
import commands
import re


import xlrd
import csv

def csv_from_excel(old, new):
	print old, new
	try:
		wb = xlrd.open_workbook(old)
		sh = wb.sheet_by_name('Sheet1')
		your_csv_file = open(new, 'wb')
		wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

		for rownum in xrange(sh.nrows):
			wr.writerow(sh.row_values(rownum))

		your_csv_file.close()
	except Exception as e:
		print "FAIL: ", e
		return


for root, dirs, files in os.walk('Census'):
	print "Current directory", root
	print "Sub directories", dirs
	for file in files:
		if not file.startswith('.'):
			newFile = os.path.join(root, file.replace(".sf1",".csv"))
			csv_from_excel(os.path.join(root, file), newFile)
			#os.rename(os.path.join(root, file), os.path.join(root,file.replace(".csv", ".xls")))

# Take all files with .xls and rename them to .csv

