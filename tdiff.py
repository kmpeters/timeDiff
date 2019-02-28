#!/usr/bin/env python3
#
# Compute the time between two camonitor timestamps
#

import datetime as dt
import re


def getTimestamp(line):
	regexStr = "20[0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]\.[0-9][0-9][0-9][0-9][0-9][0-9]"
	regex = re.compile(regexStr)
	match = regex.search(line)
	if match == None:
		retval = None
	else:
		retval = match.string[match.start():match.end()]
		#!print(retval, match.start(), match.end())
	return retval


def timeStrToObj(dt1):
	dt_format = "%Y-%m-%d %H:%M:%S.%f"
	dto1 = dt.datetime.strptime(dt1, dt_format)
	return dto1


def timeObjToStr(dto1):
	dt_format = "%Y-%m-%d %H:%M:%S.%f"
	dt1 = dt.datetime.strftime(dto1, dt_format)
	return dt1


def timeDiff(dt1, dt2):
	#!print dt1
	#!print dt2
	
	dt_format = "%Y-%m-%d %H:%M:%S.%f"
	dto1 = dt.datetime.strptime(dt1, dt_format)
	dto2 = dt.datetime.strptime(dt2, dt_format)
	
	#!print dto1
	#!print dto2
	
	tdiff = dto2 - dto1
	
	return tdiff

if __name__ == '__main__':
	import argparse as ap
	import sys
	
	parser = ap.ArgumentParser("tdiff.py")
	
	# 2019-02-20 22:27:31.493586
	# 2019-02-21 00:51:46.747478
	
	parser.add_argument("d1", action="store", default=None,  help='First date')
	parser.add_argument("t1", action="store", default=None,  help='First time')
	parser.add_argument("d2", action="store", default=None,  help='Second date')
	parser.add_argument("t2", action="store", default=None,  help='Second time')
	
	opt = parser.parse_args(sys.argv[1:])
	
	#print(opts)
	#print(vars(opt))
	
	dt1 = "{} {}".format(opt.d1, opt.t1)
	dt2 = "{} {}".format(opt.d2, opt.t2)
	
	tdiff = timeDiff(dt1, dt2)
	
	print(tdiff)
