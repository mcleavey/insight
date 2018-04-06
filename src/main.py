from user import *
from datetime import datetime
from collections import OrderedDict
import sys, logging


def translate_time(date, time):
	"""
	Translates date and time to timestamp
 	Inputs:
   		date: string in year-month-day format
   		time: string in hour:minute:second format
 	Output:
   		datetime timestamp
	"""
	return datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M:%S').timestamp()

def get_categories_to_index(line):
	"""
	Takes the first line of the csv file and outputs a dictionary translating each column heading
	name to an index
 	ie:     "ip" : 0
    	    "date" : 1
       		"time" : 2
 	Input:
   		line: string
 	Output:
   		categories_to_index: dictionary mapping column heading to index
	"""

	try:
		categories_to_index = {category: i for i, category in enumerate(line.strip().split(',')[:-1])}
	except:
		assert False, f'Error reading CSV file header: {line}'
		categories_to_index = {}

	# Check if the header has all the items we need
	# I don't see a reason we actually need cik/accession/extention for this program,
	# since we're never actually asked for the filename, but I'm leaving it here as an
	# indicator that the file has properly formed requests.  

	required = ['ip', 'date', 'time', 'cik', 'accession', 'extention']
	valid_file = True

	# Check if each required element is in the csv file
	for r in required:
		assert r in categories_to_index.keys(), f'{r} missing from CSV header'

	return categories_to_index



def get_info_from_line(line, categories_to_index):
	"""
	Pull necessary info from csv file single line
 	Inputs:
   		line: string representing the current line of the csv file
   		categories_to_index: dictionary indicating the
        	                 order of the elements of the line 
 	Output:
   		valid_line: bool if the line is in a valid format
   		current_time_stamp: current time as datetime timestamp
   		date_time: current time as string
   		ip: IP address as string
	"""

	try:
		# Split line by commas
		items = line.strip().split(',')[:-1]

		# If line doesn't have the expected number of elements, mark it invalid since we don't 
		# know how/why it is mis-formed, and the ip address may be in the wrong spot and meaningless
		valid_line = len(items) == len(categories_to_index.keys())

		current_time_stamp = translate_time(items[categories_to_index['date']], 
										   items[categories_to_index['time']])
		date_time = items[categories_to_index['date']] + ' '   \
					+ items[categories_to_index['time']]
		ip = items[categories_to_index['ip']]

	except:
		valid_line = False	
		current_time_stamp = 0
		date_time = ""
		ip = ""

	return valid_line, current_time_stamp, date_time, ip	


def process_one_line(line, categories_to_index, prev_time_stamp, inactivity, 
	                 output_file, first_request_order, expiry_to_ip, current_users):
	"""
	Take in one line. Create or update the user session for that line, and also
	output all the user sessions that have expired.
 	Inputs:
   		line: string representing the current line of the csv file
   		categories_to_index: dictionary indicating the
        	                order of the elements of the line 
   		prev_time_stamp: time stamp of previous line
   		inactivity: time in seconds after which a session is considered done
   		output_file: file opened for appending output data
   		first_request_order: int current index for this request (increases by 1 for each input line) 
   		expiry_to_ip: OrderedDict mapping expiry time to a list of IP addresses due to expire
        	         at that time
   		current_users: dictionary mapping IP address to UserSession (for IP address in an active session)
 	Output:
   		current_time_stamp: time stamp of the current line
   		(also calls output_expired_users to write the expired user sessions to file)
	"""

	# Check if this line is valid, and get the current time stamp, date-time as a string,
	# and ip address of the current request
	valid_line, current_time_stamp, date_time, ip = get_info_from_line(line, categories_to_index)

	# Exit function if this line is not valid
	if not valid_line:
		logging.warning(f'Skipping invalid file line: {line.strip()}')
		return prev_time_stamp

	if (current_time_stamp<prev_time_stamp):
		logging.warning(f'Skipping invalid file line that went backwards in time: {line.strip()}')
		return prev_time_stamp
		
	# Check if this is a new time stamp, compared with previous request
	if current_time_stamp>prev_time_stamp:
		# Initialize empty list to hold all IPs expiring at this new time
		expiry_to_ip[current_time_stamp+inactivity] = []

		# Now check which users should be output to file (unless prev_time_stamp is -1,
		# indicating this is the first time step)
		if prev_time_stamp!=-1:
			output_expired_users(current_time_stamp, prev_time_stamp, output_file, 
							     expiry_to_ip, current_users)

	# Check if this is an ongoing session
	if ip in current_users:
		# Remove this from list of sessions expiring at old expiry time
		expiry_to_ip[current_users[ip].expiry_time].remove(ip)
		# Update user session
		current_users[ip].new_request(current_time_stamp, date_time, inactivity)
		# Add to list of sessions expiring "inactivity" seconds from now
		expiry_to_ip[current_users[ip].expiry_time].append(ip)
	else:			
		# Create new user session
		current_users[ip] = UserSession(ip, date_time, current_time_stamp, 
										first_request_order, inactivity)
		# Add to list of sessions xpiring "inactivity" seconds from now
		expiry_to_ip[current_time_stamp+inactivity].append(ip)

	return current_time_stamp


def output_expired_users(current_time_stamp, prev_time_stamp, output_file, 
						 expiry_to_ip, current_users):
	""" 
	Outputs the user sessions that have timed out between prev_time_stamp and
 	current_time_stamp
 	Inputs:
   		prev_time_stamp: time stamp of previous line
   		current_time_stamp: time stamp of this line
   		output_file: file opened for appending output data
   		expiry_to_ip: OrderedDict mapping expiry time to a list of IP addresses due to expire
        	          at that time
   		current_users: dictionary mapping IP address to UserSession (for IP address
   					   in an active session)
 	Output:
   		for each expired session, writes one line to output_file
	"""

	num_to_pop = 0
	for (expiry_time, ips) in expiry_to_ip.items():
		if expiry_time<current_time_stamp:
			user_sessions_finished = [current_users[ip] for ip in ips]
			for us in sorted(user_sessions_finished):
				output_file.write(us.output())
				del current_users[us.ip]
			num_to_pop+=1
		else:
			break
	for i in range(num_to_pop):
		expiry_to_ip.popitem(last=False)


def alt_output_expired_users(current_time_stamp, prev_time_stamp, output_file, 
						 expiry_to_ip, current_users):
	""" 
	This function is not used in the program.  I wrote to Insight with a question
	about a corner case that wasn't described in the problem description.  They told
	me to select one answer (which is in output_expired_users). This is the solution
	for the other answer. I've documented this more clearly in my README
	"""
	users_timed_out = []
	num_to_pop = 0
	for (expiry_time,ips) in expiry_to_ip.items():
		if expiry_time < current_time_stamp:
			users_timed_out.extend(ips)
			num_to_pop+=1				
		else:
			break

	for i in range(num_to_pop):
		expiry_to_ip.popitem(last=False)	

	for ip in sorted(users_timed_out):
		output_file.write(current_users[ip].output())
		del current_users[ip]
	


def list_remaining(output_file, current_users):
	""" 
	At end of CSV file, output all the remaining users to output_file
 	Inputs:
   		output_file: file opened for appending output data
   		current_users: dictionary mapping IP address to UserSession (for IP address in an active session)
 	Outputs:
   		writes one line to output_file for each of the remaining user sessions
	"""

	# Collect all the users still in the currentUsers dictionary
	remaining_users = [current_users[ip] for ip in current_users]

	# Order them by initial request time and output to file
	for u in sorted(remaining_users):
		output_file.write(u.output())



def process_all_files(csv_file, inactivity_file, output_file):
	"""
 	Called directly from main(), with the arguments coming from the command line 
 	Input: 
 		csv_file: location of the file holding all the EDGAR input data
 		inactivity_file: location of the file holding the inactivity time
    	output_file: location to write output
 	Output:
   		output_file: creates (or clears) file and then writes all results to it		
	"""

	# Grab the inactivity time (after this amount of time,
	# a user is automatically assumed to have logged off)
	with open(inactivity_file) as f:
		inactivity = int(f.readline())

	# Create or clear the output file
	output=open(output_file, "w+")   
	output.close()

	current_users = {}   # key = IP
						 # value = UserSession (holds ip, times, file count for each user)
			
	first_request_order = 0  # Tracks order requests arrive (for determining order to output)

	expiry_to_ip = OrderedDict()    # key = expiry time (as timestamp)
									# value = list of IPs due to expire at that time

	# Open the output file to append one line at a time
	with open(output_file, "a") as output:
		# Open the csv file to read		
		with open(csv_file) as csv:

			# Look at the first line of the file. Make sure it has the heading
			# categories we need (otherwise this fails an assertion), and then
			# return a dictionary with category_title:index (ie "ip":0) 
			categories_to_index = get_categories_to_index(csv.readline())			

			# Read first data line
			line = csv.readline()

			# Initialize previous time stamp (set this negative, so that first line of
			# file will register as a new time stamp, later than the previous one)
			prev_time_stamp = -1			


			# Go through the csv file line by line, exit loop at EOF
			while line:
				# Feed this line to our program. If the line isn't valid, it will return the same
				# time stamp as the previous line. 
				prev_time_stamp  = process_one_line(line, categories_to_index, 
													prev_time_stamp, inactivity, output, 
													first_request_order, expiry_to_ip,
													current_users)

				# It's ok that we increment even if it's an invalid line,
				# since we only ever care about the order.
				first_request_order+=1
				
				# Read new line and continue loop				
				line = csv.readline()

		# At the end of the CSV file, output all the still active users
		list_remaining(output, current_users)


if __name__ == "__main__":
	process_all_files(sys.argv[1], sys.argv[2], sys.argv[3])