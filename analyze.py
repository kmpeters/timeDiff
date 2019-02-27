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

THRESHOLD=15.0

def getLines(log_file):
	# Try to open the log file
	try:
		fh = open(log_file, 'r')
	except IOError:
		print("{} doesn't exist.".format(log_file))
		sys.exit(1)

	# 
	relevantLine = re.compile('scan3|totalRetries')
	retryLine = re.compile("(.*totalRetries[^ ]*) *(.*-.*-.* .*:.*:.*\..*) ([0-9]+)")

	lines = []

	lastImportantTS = None
	#!lastImportantLine = None
	lastRetryTS = None
	lastRetryNum = 0

	for line in fh:
		if relevantLine.search(line) == None:
			# Consider the first line with a timestamp to be the start of the scan
			if lastImportantTS == None:
				ts = tdiff.getTimestamp(line)
				if ts != None:
					lastImportantTS = ts
					#!lastImportantLine = line[:-1]
					#!print("{}\t\t# 0:00:00.000000".format(lastImportantLine))
					lines.append((ts, 0))
		else:
			match = retryLine.search(line)
			if match != None:
				ts = match.group(2)
				num = int(match.group(3))
				
				#print(match.groups())
				#print(match.group(1))
				#print(match.group(2))
				#print(match.group(3))
				
				if lastRetryTS == None:
					# We haven't saved a timestamp yet
					lastRetryTS = ts
					lastRetryNum = num
					# This first line may be important
					lines.append((ts, num))
				else:
					# Calculate the time diff
					duration = tdiff.timeDiff(lastRetryTS, ts)
					
					# Check to see if the duration is longer than a threshhold
					threshhold = dt.timedelta(minutes=THRESHOLD)
					
					if duration > threshhold:
						# The previous item was important, add it if it wasn't added in the previous iteration
						if (lastRetryTS, lastRetryNum) not in lines:
							lines.append((lastRetryTS, lastRetryNum))
						
						# The current item is also important
						lines.append((ts, num))
						lastImportantTS = ts
					
					lastRetryTS = ts
					lastRetryNum = num
	
	fh.close()
	
	return lines[:]
	
def printLines(lines):
	#
	for i in range(0, len(lines)):
		ts = lines[i][0]
		num = lines[i][1]
		 
		if i == 0:
			print("{}\t{}\t# 0:00:00.000000 <start>".format(ts, num))
		else:
			tsp = lines[i-1][0]
			nump = lines[i-1][1]
			duration = tdiff.timeDiff(tsp, ts)
			if (num - nump) == 1:
				period = '</good>'
			else:
				period = '</bad>'
			print("{}\t{}\t# {} {}".format(ts, num, duration, period))


if __name__ == '__main__':
	#
	if len(sys.argv) != 2:
		print("Usage: analyze.py <log_file>")
	else:
		lines = getLines(sys.argv[1])
		printLines(lines)
