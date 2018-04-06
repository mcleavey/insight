from user_old import *
from datetime import date
from datetime import time
from datetime import datetime
import sys, logging

currentUserIPs = {}
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
		assert False, "CSV File Header was not valid"
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
	return cik + acc + ext

def process(line, fformat, prevTimeStamp, initTimeStamp, inactivity, index, output):
	items, currentTimeStamp = GetItemsAndTime(line, fformat)

	if len(items) != len(fformat.keys()):
		logging.warning(f'Skipping invalid file line: {line.strip()}')
		return -1

	ip = items[fformat['ip']]

	if currentTimeStamp>prevTimeStamp:
		# Don't bother checking every record unless we've passed the
		# inactivity time -- if inactivity is very large, we don't have
		# to check for it at first
		if currentTimeStamp - initTimeStamp > inactivity:
			StepTime(currentTimeStamp, inactivity, output)


#	fil = MakeFileName(items[fformat['cik']], items[fformat['accession']], items[fformat['extention']])
	fil = ""
	dtstring = items[fformat['date']] + ' ' + items[fformat['time']]

	try:
		u = currentUsers[ip]
		u.newrequest(fil, currentTimeStamp, dtstring)
			
	except:
		u = User(ip, dtstring, currentTimeStamp, fil, index)
		currentUsers[u.ip] = u

	return currentTimeStamp


def StepTime(currentTimeStamp, inactivity, output):
#Checking to see which users have timed out
#	print("StepTime")

	users = [currentUsers[key] for key in currentUsers if currentUsers[key].timeelapsed(currentTimeStamp)>inactivity]
	for u in users:
		del currentUsers[u.ip]


	for u in sorted(users):
#		print(u.output())
		output.write(u.output())


def listRemaining(output):
#At end of CSV file, output all the remaining users
#	print("ListRemaining")
	users = [currentUsers[key] for key in currentUsers.keys()]
	
	for u in sorted(users):
#		print(u.output())
		output.write(u.output())



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
			index = 0
			while line:
				newTimeStamp = process(line, csvFileFormat, prevTimeStamp, initTimeStamp, inactivity, index, output)
				if newTimeStamp == -1:
					line = csv.readline()
					continue
				prevTimeStamp = newTimeStamp
				index+=1
				
				
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