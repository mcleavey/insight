from user import *
from datetime import date
from datetime import time
from datetime import datetime
import sys, logging


currentUserIPs = []
currentUsers = {}

def TranslateTime(date, time):
	return datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M:%S').timestamp()

def setupFormat(line):
	try:
		results = {category: i for i, category in enumerate(line.strip().split(',')[:-1])}
	except:
		assert False, f'Error reading CSV file header: {line}'
		results = {}
	required = ['ip', 'date', 'time', 'cik', 'accession', 'extention']
	validfile = True
	for r in required:
		assert r in results.keys(), f'{r} missing from CSV header'
		if r not in results.keys():
			print("CSV File missing key: ", r)
			validfile = False

	if not validfile:
		print("CSV File was not valid, exiting program.")
	return results, validfile

def GetItemsAndTime(line, fformat):
	try:
		items = line.strip().split(',')[:-1]
		currentTimeStamp = TranslateTime(items[fformat['date']], items[fformat['time']])
	except:
		items = []
		currentTimeStamp = -1
	return items, currentTimeStamp	

def MakeFileName(cik, acc, ext):
	return cik + acc + ext, cik, acc, ext

def process(line, fformat):
	items, currentTimeStamp = GetItemsAndTime(line, fformat)
	if len(items) != len(fformat.keys()):
		logging.warning(f'Skipping invalid file line: {line.strip()}')
		return -1
	fil = MakeFileName(items[fformat['cik']], items[fformat['accession']], items[fformat['extention']])
	dtstring = items[fformat['date']] + ' ' + items[fformat['time']]
	if (items[fformat['ip']] in currentUserIPs):
		u = currentUsers[items[fformat['ip']]]
		u.newrequest(fil, currentTimeStamp, dtstring)
	else:
		u = User(items[fformat['ip']], dtstring, currentTimeStamp, fil)

		currentUserIPs.append(u.ip)
		currentUsers[items[fformat['ip']]] = u
	return currentTimeStamp

def StepTime(currentTimeStamp, inactivity, output):
#	print("Checking to see which users have timed out")
	
	for idx, ip in enumerate(currentUserIPs):
		u = currentUsers[ip]
		if u.timeelapsed(currentTimeStamp) > inactivity:
			output.write(u.output())
			del currentUserIPs[idx]

def listRemaining(output):
# At end of CSV file, output all the remaining users
	for ip in currentUserIPs:
		output.write(currentUsers[ip].output())

def ReadLines(csv_file, inactivity_file, output_file):
# Read inactivity_file to get inactivity delay time
# Read each individual line of the csv_file
# Output results to output file

	# Grab the inactivity time (after this amount of time,
	# a user is automatically assumed to have logged off)
	with open(inactivity_file) as f:
		inactivity = int(f.readline())

	# Create or clear the output file
	f=open(output_file, "w+")   
	f.close()
	with open(output_file, "a") as output:
		with open(csv_file) as csv:
			csvFileFormat, validfile = setupFormat(csv.readline())
			if not validfile:
				return
			line = csv.readline()
			_, initTimeStamp = GetItemsAndTime(line, csvFileFormat)
			prevTimeStamp = initTimeStamp

			while line:
				newTimeStamp = process(line, csvFileFormat)
				if newTimeStamp == -1:
					line = csv.readline()
					continue
			
				if newTimeStamp>prevTimeStamp:
					prevTimeStamp = newTimeStamp

					# Don't bother checking every record unless we've passed the
					# inactivity time -- if inactivity is very large, we don't have
					# to check for it at first
					if newTimeStamp - initTimeStamp > inactivity:
						StepTime(newTimeStamp, inactivity, output)
				
				line = csv.readline()

		# At the end of the CSV file, output all the still active users
		listRemaining(output)

if __name__ == "__main__":
	ReadLines(sys.argv[1], sys.argv[2], sys.argv[3])

	# TODO:
	# Check if inactivity int stays within range (what if it's 80000)
	# Add comments
	# Look for corner cases
	# Think about scaling
	# Add separate input/output files as arguments