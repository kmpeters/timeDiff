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


# Threshold in minutes for failures to belong to a new period
THRESHOLD=15.0
# Tolerance in seconds for periods to be considered the same
TOLERANCE=90.0

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
	print ("Significant Events:")
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
	print()


def computeDurations(lines):
	#
	durations = []
	
	for i in range(0, len(lines)):
		ts = lines[i][0]
		num = lines[i][1]
		 
		if i == 0:
			pass
		else:
			tsp = lines[i-1][0]
			nump = lines[i-1][1]
			duration = tdiff.timeDiff(tsp, ts)
			failures = num - nump
			if failures == 1:
				period = 'good'
			else:
				period = 'bad'
			durations.append({'end':ts, 'start':tsp, 'duration':duration, 'period':period, 'failures':failures})
	
	return durations[:]


def printDurations(durations):
	for d in durations:
		# Show microseconds
		#!print("{} - {} : {} {} period ({} failures)".format(d['start'], d['end'], d['duration'], d['period'], d['failures']-1))
		# Don't show microseconds
		print("{} - {} : {} {} period ({} failures)".format(d['start'][:-7], d['end'][:-7], d['duration'], d['period'], d['failures']-1))


def printHistory(durations):
	print("Scan History:")
	printDurations(durations)
	print()


def computePredictions(durations, numPeriods=10):
	#
	predictions = []
	# List of timedelta objects
	durationList = [d['duration'] for d in durations]
	# List of durations in seconds
	secondsList = [d.total_seconds() for d in durationList]
	#!print(durationList)
	#!print(secondsList)
	
	# Subtract the last period from each item in the list to see
	# how many periods there are before the pattern repeats.
	tempList = [t - secondsList[-1] for t in secondsList]
	#!print(tempList, len(tempList))
	# Find the zeros in the list
	i = 0
	zeroes = []
	while i < len(tempList):
		if abs(tempList[i]) <= TOLERANCE:
			zeroes.append(i)
		i += 1
	#!print(zeroes)
	# Use the last full iteration of the pattern to make the predictions
	patternStart = zeroes[-2]+1
	# The last element in the zeroes list is the index of the last duration
	patternEnd = zeroes[-1]
	patternDurations = durations[patternStart:]
	#!print(patternDurations, patternEnd)
	# The predictions start at the end of the pattern
	predictionStart = durations[patternEnd]['end']
	#!print("Sanity check", durations[patternEnd])
	#!print(predictionStart)
	i = 0
	predictions = []
	ps = tdiff.timeStrToObj(predictionStart)
	while i < numPeriods:
		iDur = patternDurations[i % len(patternDurations)]['duration']
		iPer = patternDurations[i % len(patternDurations)]['period']
		iFail = patternDurations[i % len(patternDurations)]['failures']
		pe = ps + iDur
		predictions.append({'end':tdiff.timeObjToStr(pe), 'start':tdiff.timeObjToStr(ps), 'duration':iDur, 'period':iPer, 'failures':iFail})
		ps = pe
		i += 1
	
	return predictions


def printPredictions(predictions):
	print("Predictions:")
	printDurations(predictions)
	print()


if __name__ == '__main__':
	#
	numArgs = len(sys.argv)
	
	if numArgs not in (2, 3):
		print("Usage: analyze.py <log_file> [prediction_periods]")
	else:
		lines = getLines(sys.argv[1])
		printLines(lines)
		durations = computeDurations(lines)
		printHistory(durations)
		if numArgs == 3:
			predictions = computePredictions(durations, int(sys.argv[2]))
		else:
			predictions = computePredictions(durations)
		printPredictions(predictions)
