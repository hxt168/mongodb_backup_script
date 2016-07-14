import os
class LockCheck:
	lock_name= ""
	def __init__(self, ):
		self.lock_name = os.path.split(os.path.realpath(__file__))[0]+"/backup.lock"

	def is_lock(self):
		if os.path.exists(self.lock_name):
			return True;
		else:
			return False;
	
	def lock(self):
		if not self.is_lock():
			print "lock.."
			lock_file = open(self.lock_name, 'w')
			try:
				lock_file.write("")
			except Exception, e:
				raise e
			finally:
				lock_file.close()
				
	def release(self):
		if self.is_lock():
			print "release lock.."
			os.remove(self.lock_name)