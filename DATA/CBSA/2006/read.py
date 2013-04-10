import csv


with open('CBSABook11.csv', 'rb', 'utf-8') as csvfile:
	
	spamreader = csv.reader(csvfile, dialect='excel')
	for row in spamreader:
		if row != NULL:
			print ', '.join(row)
