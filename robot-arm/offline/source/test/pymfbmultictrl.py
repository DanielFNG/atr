#!/usr/bin/env python
# encoding: utf-8
"""
pymfbmultictrl.py

Created by t_noda on 2013-08-07.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
sys.path.append("../pydrivers/")
import os
import unittest
import time
from pydrvmfb import pydrvmfb 

# trying to import xenomodule
try:
	import xenomodule
except:
	print "xenomai module load faild (probably not found)"

class pymfbmultictrl:
	def __init__(self):
		self.mfbs = []
		self.sizes = []
	def add_mfb(self,mfb):
		self.mfbs.append(mfb)  
		self.sizes.append(0)
	def get_prepare(self, request=True):
		for mfb in self.mfbs: 
			mfb.select_switch([0,1,0,0])
			mfb.generatebuf()
                if request==True:
                        for mfb in self.mfbs: 
                                mfb.request()
	def clearbuf(self):
		for mfb in self.mfbs: 
			for j in range(100):
				res = mfb.readdata(request = False)
				if res < 0:
					break
	def get(self, f_debug=True):
		for mfb, num in zip(self.mfbs, range(len(self.mfbs))):
			self.sizes[num] = mfb.readdata(request = False)
			if self.sizes[num]>0:
				#import pdb;pdb.set_trace()
				mfb.decodebuf()
			else:
				if f_debug==True:
					print "warning:--------timeout for mfb%d size %d -----------" % (num, self.sizes[num])
		return self.sizes

	def put_prepare(self):
		for mfb in self.mfbs : 
			mfb.select_switch([1,0,1,0])
			mfb.generatebuf()

	def put(self):
		for mfb in self.mfbs : 
			mfb.request()

	def put_post(self):
		for mfb, num in zip(self.mfbs, range(len(self.mfbs))):
			self.sizes[num] = mfb.readdata(request = False)
			if self.sizes[num]>0:
				pass
			else:
				print "warning:--------timeout for mfb%d size %d -----------" % (num, self.sizes[num])
		return self.sizes

if __name__ == '__main__':

	xeno=xenomodule.xenomodule()
	xeno.mlockall()
	xeno.rt_task_shadow("Task 1", 99, 0)
	xeno.rt_task_set_periodic(4000000) # 4msec loop
	print 'Enter Xenomai'

	timeout = 1000000 # 1msec
	drvmfb1 = pydrvmfb(host="192.168.201.2", port=10008, testflag=False, RTNET=True, TIMEOUT = timeout)
	drvmfb2 = pydrvmfb(host="192.168.200.2", port=10007, testflag=False, RTNET=True, TIMEOUT = timeout)

	mfbmultictrl = pymfbmultictrl()
	mfbmultictrl.add_mfb(drvmfb1)
	mfbmultictrl.add_mfb(drvmfb2)
	for i in xrange(10):
		mfbmultictrl.get_prepare()
        mfbmultictrl.get()
	print drvmfb1.realvalue['counter'][2]
        print "get done."
        drvmfb1.realvalue['da'][0] = float(i)
        mfbmultictrl.put_prepare()
        mfbmultictrl.put()
        mfbmultictrl.put_post()
        print "put done."
        time.sleep(0.01)
	print "done."
