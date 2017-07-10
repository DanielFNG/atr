#!/usr/bin/env python
# encoding: utf-8
"""
pydrvmfb.py

Created by noda on 2012-05-08.
Copyright (c) 2012  All rights reserved.
"""

import sys
import os
import unittest
#import pexpect
import socket
import struct
import array
import time
NOT_FOUND_ART = False
try:
	import art
except ImportError:
	NOT_FOUND_ART = True
	pass

NOT_FOUND_RTNET = False
try:
	import xenomodule
	import rtnetmodule
except ImportError:
	NOT_FOUND_RTNET = True
	pass

import numpy as np
import scipy.io

#ENC_TICKS_PER_TURN = (220092.0)
ENC_TICKS_PER_TURN =  (5. / 2. * 23. * 4000.)  ## --> 230000.0
ENC2RAD	 = ((2.0 * np.pi) / ENC_TICKS_PER_TURN)

class pydrvmfb:
	"""
	Multi Function Board Driver:

	Discription: 
	This 

	"""
	def __init__(self, ART_on=False, testflag=False, host="192.168.200.2", port=10007, RTNET=False, TIMEOUT=0 ):
		self.RTNET = RTNET
		self.TIMEOUT = TIMEOUT
		self.starttime = time.time()
		self.testflag = testflag
		self.n_ch={
			"da":16,
			"IO_in":1,
			"switch":4,
			"dummy_out1":7,
			"dummy_out2":6,
			"dummy_out3":8,
			"ad":16,
			"counter":8,
			#"idx_counter":8,
			"IO_out":1,
			"dummy_in":7,
			"dummy_ext_out":16,
			"dummy_ext_in":16,
			}
		self.fmt4key={
			"da":'h',
			"IO_in":'h',
			"switch":'b',
			"dummy_out1":'h',
			"dummy_out2":'h',
			"dummy_out3":'h',
			"ad":'h',
			"counter":'I',
			"IO_out":'h',
			"dummy_in":'h',
			"dummy_ext_out":'h',
			"dummy_ext_in":'h',
			}
		self.scale={
			"da": 10.0 / float(0x7fff),
			"IO_in":1.,
			"switch":1.,
			"dummy_out1":1.,
			"dummy_out2":1.,
			"dummy_out3":1.,
			"ad":10.0/ float(0x7fff),
			#"counter":1./float(0xfffff),
			"counter": ENC2RAD,
			"IO_out":1.,
			"dummy_in":1.,
			"dummy_ext_out":1.,
			"dummy_ext_in":1.,
			}
		self.offset={
			"da":0,
			"IO_in":0,
			"dummy_out1":0,
			"switch":0,
			"dummy_out2":0,
			"dummy_out3":0,
			"ad":0,
			"counter":0x80000000,
			"IO_out":0,
			"dummy_in":0,
			"dummy_ext_out":0,
			"dummy_ext_in":0,
			}

		self.fmtorder_out = ["da", "IO_out", "dummy_out1", "switch", "dummy_out2", "dummy_out3", "dummy_ext_out"]
		self.fmtorder_in = ["ad", "counter", "IO_in", "dummy_in", "dummy_ext_in"]
		self.fmt4pack={
			}
		self.value = {
			}
		self.realvalue = {
			}
		#self.minRealValues = np.array([0.0 for j in range(self.n_ch['da'])])
                #self.maxRealValues = np.array([+5.0 for j in range(self.n_ch['da'])])
		#self.safevalue = self.minRealValues
                #self.setDAMinMax()



		# generate init value and format
		for k, v in self.n_ch.iteritems():
			self.value[k] = np.zeros(v, dtype=self.fmt4key[k])
			self.realvalue[k] =  np.zeros(v)
			## little edian by default
			fmt = "<" + self.fmt4key[k] * v
					
			self.fmt4pack[k] =fmt

		bufsize_out = 0
		for k in self.fmtorder_out:
			print "size of ", self.fmt4pack[k] , "is", struct.calcsize(self.fmt4pack[k]) 
			bufsize_out += struct.calcsize(self.fmt4pack[k])
		bufsize_in = 0
		for k in self.fmtorder_in:
			bufsize_in += struct.calcsize(self.fmt4pack[k])
		#self.buf = '\0x00'* bufsize
		print 'bufsize_in=', bufsize_in
		print 'bufsize_out=', bufsize_out

		self.bufarray_in = ""
		self.bufarray_out = array.array('c', ' ' * bufsize_out)

		#self.fmtxmlin=["ad", "counter", "IO_in", "dummy_in"]
		self.host1 = host
		self.port1 = port

		# if self.testflag==False:
		if self.RTNET == True:
			self.s=rtnet=rtnetmodule.rtnetmodule()
			#self.s = rtnet.mysocket()
			self.s.RTnet_init(self.port1,self.host1,self.port1,self.TIMEOUT)
		else:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.s.connect((self.host1, self.port1))
		self.size=0
	def testswitch(self, flag):
		"""
		Call this function beforegeneratebuf() to test switch 
		"""
		# ------ use this if not work ---
		#k = "switch"
		#p_buf = 0x30 
		#struct.pack_into(self.fmt4pack[k], self.bufarray_out, p_buf, 0, 0, 0, 1)

		# ------------- test -------------
		# test AD off / on
		#self.realvalue["switch"][0]= 1. # off 
		#self.realvalue["switch"][0]= 0. # on 

		# test DA off / on
		#self.realvalue["switch"][1]= 1.# off
		#self.realvalue["switch"][1]= 0.# on  
		# test Counter off / on
		#self.realvalue["switch"][2]= 1.
		#self.realvalue["switch"][2]= 0.
		# test IO off / on
		#self.realvalue["switch"][3]= 1.
		#self.realvalue["switch"][3]= 0.
		self.realvalue['switch'][:] = flag[:]

	def select_switch(self, flag):
		"""
		Call this function before generatebuf() to test switch 
		"""
		# ------ use this if not work ---
		#k = "switch"
		#p_buf = 0x30 
		#struct.pack_into(self.fmt4pack[k], self.bufarray_out, p_buf, 0, 0, 0, 1)

		# ------------- test -------------
		# test AD off / on
		#self.realvalue["switch"][0]= 1. # off 
		#self.realvalue["switch"][0]= 0. # on 

		# test DA off / on
		#self.realvalue["switch"][1]= 1.# off
		#self.realvalue["switch"][1]= 0.# on  
		# test Counter off / on
		#self.realvalue["switch"][2]= 1.
		#self.realvalue["switch"][2]= 0.
		# test IO off / on
		#self.realvalue["switch"][3]= 1.
		#self.realvalue["switch"][3]= 0.
		self.realvalue['switch'][:] = flag[:]


	def generatebuf(self):
		p_buf =  0
		for k in self.fmtorder_out:
			# pack the value into buffer
			self.value[k] = self.realvalue[k]/self.scale[k] - self.offset[k]
			#print "value", self.value[k] 
			struct.pack_into(self.fmt4pack[k], self.bufarray_out, p_buf, *np.round(self.value[k]).astype(self.fmt4key[k]))
			#print "fmt4pack", self.fmt4pack[k] 
			#print "bufarray_out", self.bufarray_out 
			p_buf +=  struct.calcsize(self.fmt4pack[k])
			#print "p_buf", p_buf


		#print self.bufarray_out
	def myrand(self,k):
		return  float(0x7fff)* (np.sin((time.time()-self.starttime)*2.*np.pi) /2.0 + 0.1* np.random.rand(self.n_ch[k]))
	def generatedummybuf_in(self):
		p_buf =  0
		for k in self.fmtorder_in:
			# pack the value into buffer
			dummydata = self.myrand(k)
			#dummydata = np.sin(time.time()) + 0.1* np.random.rand(self.n_ch[k])
			# struct.pack_into(self.fmt4pack[k], self.bufarray_out, p_buf, *np.round(self.value[k]).astype(self.fmt4key[k]))
			struct.pack_into(self.fmt4pack[k], self.bufarray_out, p_buf, *self.value[k].astype(self.fmt4key[k]))
			p_buf +=  struct.calcsize(self.fmt4pack[k])
			#import pdb; pdb.set_trace()
		
	def decodebuf(self):
		if self.testflag==True:
			pass			
		else:
			p_buf = 0
			# decode buffer to float
			for k in self.fmtorder_in:
				# unpack value into buffer
				self.value[k][0:self.n_ch[k]] =  np.array(struct.unpack_from(self.fmt4pack[k], self.bufarray_in, offset=p_buf))
				self.realvalue[k] = self.scale[k] * (self.value[k].astype('float64') - self.offset[k])
				p_buf += struct.calcsize(self.fmt4pack[k])

	def request(self):
		#print self.bufarray_out
		if(self.RTNET==True):
			self.s.rt_send(self.bufarray_out.tostring(), )
		else:
			self.s.sendall(self.bufarray_out.tostring())
	def readdata(self, buf=None, request=True):
		self.size=0
		if self.testflag==True:
			# Generate a dummy data for AD
		        # self.generatedummybuf_in()
			self.size=1
			pass
			#self.recieved = struct.pack(self.formatting, *tuple(dummydata))
			#print len, len(self.recieved)
		else:
			if(buf):
			        #print "custombuf"
				if(self.RTNET==True):
					self.s.rt_send(buf,)
				else:
					self.s.sendall(buf)
			else:
				#print "sending..."
				#self.s.sendall("test")				
				if (request == True):
					if(self.RTNET==True):
						self.s.rt_send(self.bufarray_out.tostring(),)
					else:
						self.s.sendall(self.bufarray_out.tostring())
				else:
					pass
				#import pdb; pdb.set_trace()
				#self.s.sendall(' '*64)
				#self.s.sendall(struct.pack('>'+''.join(['h' for j in range(32)]), *[0 for j in range(32)])) 
				#print "done"
				#print "waiting for data recieved...",
				#sys.stdout.flush()
				if self.RTNET== True:
					self.bufarray_in, self.size = self.s.rt_recv()
				else:

					self.bufarray_in = self.s.recv(8192)
					self.size = len(self.bufarray_in)

					#print len(self.bufarray_in)
				#print "done."

			#print "self.recieved=", self.recieved
			#print len, len(self.recieved)

		#res = struct.unpack(self.format, self.recieved)
		#import pdb; pdb.set_trace()
		#print self.fmt % tuple(map(lambda x: float(x)*10./float(0x10000),res))

		return self.size

class PyDrvMbedTests(unittest.TestCase):		
	def setUp(self):
		#self.host = "192.168.0.100"
		self.host = "192.168.200.2"
		self.skip = False
		#self.ART_on = True
		self.ART_on = False
		self.n_ch = 16
		self.fmt = "("+"".join("%f, " for j in range(self.n_ch)) +")"
		
	def testLoop100times(self):
		print "testing 10 times read from mbed."
		drvmbed = pydrvmbedmulti()
		for t in range(10):
			res = drvmbed.readdata()
			print self.fmt % tuple(map(lambda x: float(x)*10./float(0x10000),res))
			time.sleep(0.01)
			
	def testLoopART(self, freq_ctrl=100.0, exptime=1.0):
		"""
		ART 100 times loop
		"""	
		print "testing 10 times ART read from mbed..."
		nloop = int(freq_ctrl*exptime)
		drvmbed = pydrvmbedmulti()
		results = np.zeros((nloop, self.n_ch))
		times = np.zeros(nloop)
		if self.ART_on==True:
			waitutime = 1000000/freq_ctrl
			print ("Entering to ART process by wait time = ", waitutime, "[usec]")
			art.art_enter(art.ART_PRIO_MAX, art.ART_TASK_PERIODIC, waitutime)
		for t in range(nloop):
			times[t] = time.time()
			#value = [(float(t)/nloop * float(0x1000) - 0x7ff ) for j in range(self.n_ch) ]
			value = [(float(t)/nloop * float(0x7ff) ) for j in range(self.n_ch) ]
			value[1] = 1. * value[1]
			value[0] = 1. * value[0]
			buf = drvmbed.getbuf(value)
			#print value
			results[t,:] = np.array(drvmbed.readdata(buf=buf))
			if self.ART_on == True:	
				art.art_wait()
			else:
				time.sleep(1./freq_ctrl)
		scipy.io.savemat('./test/ad-da-test.mat', {'test':results})
		
			##
		if self.ART_on==True:
			art.art_exit()
		print self.fmt % tuple(map(lambda x: float(x)*10./float(0x7fff), tuple(results.mean(axis=0))))
		print results * 10./float(0x7fff)
		import pylab
		pylab.plot(results*10./float(0x7fff))
		pylab.xlabel('sampling [-]')
		pylab.ylabel('voltage [V]')
		pylab.title('AD sampling result')
		pylab.show()
		
	def testSetZero(self):		
		drvmbed = pydrvmbedmulti()
		value = [0 for j in range(self.n_ch) ]
		buf = drvmbed.getbuf(value)
		drvmbed.readdata(buf=buf)

if __name__ == '__main__':

	freq_ctrl = 1000
	SMP_TIME = 1000000000/freq_ctrl
	#timeout = SMP_TIME/100
	timeout = -1
	xeno=xenomodule.xenomodule()
	xeno.mlockall()
	xeno.rt_print_auto_init()
	xeno.rt_task_shadow("Task 1", 99, 0)
	xeno.rt_task_set_periodic(SMP_TIME)

	# drvmfb = pydrvmfb(host="192.168.200.2", port=10007)
	drvmfb = pydrvmfb(host="192.168.200.2", port=10007, testflag=False, RTNET=True, TIMEOUT=timeout)
	#drvmfb = pydrvmfb(host="localhost", port=19990)
	#drvmfb = pydrvmfb()
	nloop = 10
	for i in xrange(nloop):
		drvmfb.realvalue['da'][0:16] = np.zeros(16)
		# test for switch
		#flag = np.zeros(4)
		#flag = np.ones(4)
		flag = np.array((1,1,1,0))
		drvmfb.testswitch(flag)
		t1 = time.time()
		drvmfb.generatebuf()
		t3 = time.time()
		size = drvmfb.readdata()
		t4 = time.time()
		# print size
		drvmfb.decodebuf()
		t2 = time.time()
		print (t2-t1)*1000,'[ms]'
		print (t4-t3)*1000,'[ms]'

	#drvmfb.value['da'][0] = 0x6061
	#drvmfb.generatebuf()
	#drvmfb.readdata()
	print "main done"
	
