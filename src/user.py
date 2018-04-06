class UserSession:
	"""	
	Defines one session for one user. We create a new UserSession for each
	initial request from an IP address. It tracks all the info that will be
	needed for the output line, as well as the expected expiry time
	(latest request time + inactivity time)  

	From the README description, it seems we don't actually need
	to know the file name of requests to solve the problem (we don't output this,
	and we count every request, even if it's for the same file).
	If we wanted to track file names, we could add a list self.files = [first_file] and
	add to it at each new_request 
	"""

	def __init__(self, ip, date_time, current_time_stamp, index, inactivity):
		"""
		Inputs:
			ip: IP address as string
			date_time: current time in the string format required for output
			current_time_stamp: current time as datetime timestamp
			index: int to track the order in which this session's first request arrived
			inactivity: seconds until user session should be considered finished
		"""
		self.ip = ip
		self.first_request_time = date_time                    
		self.last_request_time = date_time
		self.expiry_time = current_time_stamp + inactivity
		self.init_time_stamp = current_time_stamp
		self.session_length = 1
		self.num_requests = 1
		self.initial_request_order = index


	def __lt__(self, other):
		"""
		For sorting UserSessions in order of which had the earliest initial request
		"""
		return self.initial_request_order<other.initial_request_order
		

	def new_request(self, current_time_stamp, date_time, inactivity):
		"""
		When the same UserSession has another request. Updates the items needed for the
		output data (last_request_time, session_length, and num_requests).
		Also update the expected expiry time for this session (if no more requests come
		in, it will be inactivity seconds from this current timestamp)
		Inputs:
			current_time_stamp: current time as datetime timestamp
			date_time: current time in the string format required for output
			inactivity: seconds until user session should be considererd finished
		"""
		self.last_request_time = date_time
		self.expiry_time = current_time_stamp + inactivity
		self.session_length = current_time_stamp - self.init_time_stamp + 1
		self.num_requests += 1

	def output(self):
		"""
		Format the output. This produces the string that will be written to the output file
		when the UserSession times out.
		"""
		return self.ip + ','                       \
		     + self.first_request_time + ','       \
		     + self.last_request_time + ','        \
		     + "%d"%(self.session_length)          \
		     + ',' + str(self.num_requests) + '\n'