#!/usr/bin/env python
# encoding: utf-8
"""
pyrealtime.py

Created by t_noda on 2013-06-26.
Copyright (c) 2013  All rights reserved.


how to use this script (test):
  sudo ipython --pylab=qt -i   ./pyrealtime.py 
"""

import sys
import os
import unittest
import time
import numpy
ONE_SEC_BY_NANO = 1000000000
SMP_FREQ_DEFAULT = 250
try:
	import xenomodule
except:
	xenomodule = None
	print "xenomai module load faild (probably not found)"

class pyrealtime:
	def __init__(self, f_xenomai=True, SMP_FREQ=SMP_FREQ_DEFAULT):
		self.freq_ctrl = SMP_FREQ
		self.f_xenomai = f_xenomai
		self.SMP_TIME = ONE_SEC_BY_NANO/SMP_FREQ
		print self.SMP_TIME
		print "hai"
		#print "sampling time..."
		#print int(self.SMP_TIME), "nano sec"
		#print int(self.SMP_TIME/1000), "micro sec"
		#print int(self.SMP_TIME/1000), "ms"

	def init_realtime(self):

		if self.f_xenomai == True:
			self.xeno=xenomodule.xenomodule()
			self.xeno.mlockall()

			self.xeno.rt_print_auto_init()

			#self.xeno.rt_print_init(4096, "Task 1")

			self.xeno.rt_task_shadow("Task 1", 99, 0)
			#self.xeno.rt_task_set_periodic(self.SMP_TIME)
			self.xeno.rt_task_set_periodic(int(self.SMP_TIME))
			self.prevtime = self.stime =self.xeno.rt_timer_read()
			#print 'Enter Xenomai'
			#self.xeno.rt_printf("te-----------")
			print "test" 
		else:
			pass


	def wait(self):
		if self.f_xenomai == True:
			ret=self.xeno.rt_task_wait_period()

		else:
			print "non realtime"
			ret=time.sleep(1./self.freq_ctrl)
		return ret
	def readlaptime(self):
		if self.f_xenomai == True:

			now = self.xeno.rt_timer_read()
		else:
			print "non realtime"
			self.prevtime = now =time.time()
		lap = (now - self.prevtime) * 1e-9
		self.prevtime = now
		return lap
	def readtime(self):
		if self.f_xenomai == True:
			now = self.xeno.rt_timer_read()
		else:
			print "non realtime"
			self.prevtime = now =time.time()
		return now
	def get_smpltime(self):
		return self.SMP_TIME

class pyrealtimeTests(unittest.TestCase):
	def setUp(self):
		self.freq = 1000
		self.rtmodule = pyrealtime(SMP_FREQ=self.freq)
		self.rtmodule.init_realtime()
	def test_realtimeloop(self):
		exptime = 3
		nloop = self.freq * exptime
		print "enter rt"
		lap=numpy.zeros(nloop)
		for j in range(nloop):
			self.rtmodule.wait()
			lap[j] = self.rtmodule.readtime()
			#self.rtmodule.rtprint("Ct= %d : Hello RT world!\n" %  j)
						


		print lap
		# from pylab import plot, show
		# print "plot..."
		plot(lap)
		#show()

	# def test_realtimeprint(self):
	# 	freq = 250
	# 	exptime = 1
	# 	loop = freq * exptime
	# 	print "into reatime loop"
	# 	#rtmodule.init_realtime()
	# 	for j in range(loop):
	# 		self.rtmodule.wait()
	# 		print "test"



if __name__ == '__main__':
	unittest.main()
