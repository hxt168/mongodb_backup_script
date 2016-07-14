#!/usr/bin/env

class Properties:
	fileName = ''
	def __init__(self, fileName):
		self.fileName = fileName

	def getProperties(self):   
		try:
			pro_file = open(self.fileName, 'r')
			properties = {}
			for line in pro_file:
				if line.find('=') > 0 and line.find('#') < 0:
					strs = line.replace('\n', '').split('=')
					p_key=strs[0].strip()
					p_value=strs[1].strip()
					properties[p_key] = p_value
		except Exception, e:
			raise e
		finally:
			pro_file.close()
		return properties