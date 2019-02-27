#!/usr/bin/env python3
#
# Analyze caMonitor logs from saveData troubleshooting
#

import sys
import re

def main(log_file):
	# Try to open the log file
	try:
		fh = open(log_file, 'r')
	except IOError:
		print("{} doesn't exist.".format(log_file))
		sys.exit(1)

	# 
	relevantLine = re.compile('scan3|totalRetries')

	for line in fh:
		if relevantLine.search(line) != None:
			print(line[:-1])

if __name__ == '__main__':
	#
	if len(sys.argv) != 2:
		print("Usage: analyze.py <log_file>")
	else:
		main(sys.argv[1])
