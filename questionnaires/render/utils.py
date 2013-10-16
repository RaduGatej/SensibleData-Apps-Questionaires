import re

def htmlize(string):
	return re.sub('[^a-z_0-9-:]','',string.strip().lower().replace(' ','_'));
