class UserNode:
	def __init__(self, user=None, parent=None, child=None):
		self.user = user
		self.parent = parent
		self.child = child

class User:
	def __init__(self, ip, dtstring, timestamp, fil, index, inactivity=0):
		self.ip = ip
		self.firstRequestTime = dtstring
		self.lastRequestTime = dtstring
		self.lastRequestTimeStamp = timestamp
		self.expiryTime = timestamp + inactivity
		self.initTimeStamp = timestamp
		self.file = [fil]
		self.numRequests = 1
		self.outputOrder = index

	def __lt__(self, other):
		return self.outputOrder<other.outputOrder
		
	def describe(self):
		print(f'IP: {self.ip}')
		print(f'Initial time: {self.firstRequestTime}')
		print(f'Initial time stamp: {self.initTimeStamp}')

	def timeelapsed(self, currentTimeStamp):
		return int(currentTimeStamp - self.lastRequestTimeStamp) 

	def newrequest(self, file, currentTimeStamp, dtstring, inactivity=0):
		#As far as I can tell from the instructions, we don't actually need
		#to know the file name (it says we consider it a new request, even
		#if it's the same file). I'm leaving this in for now, in case I've
		#misinterpreted it. It shouldn't add a lot of extra time relative to
		#everything else.
		self.file += file
		self.lastRequestTime = dtstring
		self.lastRequestTimeStamp = currentTimeStamp
		self.expiryTime = currentTimeStamp + inactivity
		self.numRequests += 1

	def output(self):
		return self.ip + ','                                               \
		     + self.firstRequestTime + ','                                 \
		     + self.lastRequestTime + ','                                  \
		     + "%d"%(self.lastRequestTimeStamp - self.initTimeStamp + 1)   \
		     + ',' + str(self.numRequests) + '\n'