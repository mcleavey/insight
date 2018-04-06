class User:
	def __init__(self, ip, dtstring, timestamp, fil):
		self.ip = ip
		self.firstRequestTime = dtstring
		self.lastRequestTime = dtstring
		self.lastRequestTimeStamp = timestamp
		self.initTimeStamp = timestamp
		self.file = [fil[0]]
		self.numRequests = 1

	def describe(self):
		print(f'IP: {self.ip}')
		print(f'Initial time: {self.firstRequestTime}')
		print(f'Initial time stamp: {self.initTimeStamp}')

	def timeelapsed(self, currentTimeStamp):
		return int(currentTimeStamp - self.lastRequestTimeStamp) 

	def newrequest(self, file, currentTimeStamp, dtstring):
		self.file += file
		self.lastRequestTime = dtstring
		self.lastRequestTimeStamp = currentTimeStamp
		self.numRequests += 1

	def output(self):
		return self.ip + ','                                               \
		     + self.firstRequestTime + ','                                 \
		     + self.lastRequestTime + ','                                  \
		     + "%d"%(self.lastRequestTimeStamp - self.initTimeStamp + 1)   \
		     + ',' + str(self.numRequests) + '\n'