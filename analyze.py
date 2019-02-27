#!/usr/bin/env python3
#
# Analyze caMonitor logs from saveData troubleshooting
#

# kmpSD2:saveData_totalRetries   <undefined> 0 UDF INVALID
# kmpSD2:saveData_totalRetries   2019-02-26 09:38:28.746452 1  
# kmpSD2:scan3.CPT               2019-02-26 09:32:51.995168 1  


import sys
import re
import tdiff
import datetime as dt


def main(log_file):
	# Try to open the log file
	try:
		fh = open(log_file, 'r')
	except IOError:
		print("{} doesn't exist.".format(log_file))
		sys.exit(1)

	# 
	relevantLine = re.compile('scan3|totalRetries')
	retryLine = re.compile('totalRetries')
	lastRetryTimestamp = None
	lastRetryLine = None
	lastImportantTS = None
	lastImportantLine = None
	lastDuration = None

	for line in fh:
		if relevantLine.search(line) != None:
			#!print(line[:-1])
			
			if retryLine.search(line) != None:
				# Line is a retry line
				
				# Get the line's timestamp
				ts = tdiff.getTimestamp(line)
				if ts == None:
					# line doesn't have a timestamp (should only happen on connect/disconnect)
					continue
				
				if lastRetryTimestamp == None:
					# We haven't saved a timestamp yet
					lastRetryTimestamp = ts
					lastRetryLine = line[:-1]
					lastImportantTS = ts
					lastImportantLine = line[:-1]
				else:
					# Calculate the time diff
					duration = tdiff.timeDiff(lastRetryTimestamp, ts)
					
					# Check to see if the duration is longer than a threshhold
					threshhold = dt.timedelta(minutes=5.0)
					
					if duration > threshhold:
						lastDuration = tdiff.timeDiff(lastImportantTS, lastRetryTimestamp)
						print("{}\t\t# {}".format(lastRetryLine, lastDuration))
						
						print("{}\t\t# {}".format(line[:-1], duration))
						lastImportantTS = ts
						lastImportantLine = line[:-1]
					#
					lastRetryTimestamp = ts
					lastRetryLine = line[:-1]
				
				#!print(tdiff.getTimestamp(line))
	
	fh.close()


if __name__ == '__main__':
	#
	if len(sys.argv) != 2:
		print("Usage: analyze.py <log_file>")
	else:
		main(sys.argv[1])
