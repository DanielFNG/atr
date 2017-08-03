#!/usr/bin/env python
# encoding: utf-8
"""
LoggerTemplate.py

Created by Tomoyuki Noda on 2013-08-05.
Copyright (c) 2013 . All rights reserved.

This is the template for logging data
"""

import sys
sys.path.append("../../../pydrivers/")
sys.path.append("../../")
sys.path.append("../")
#from DrvEMG import DrvEMG
#from pydrvmfb import pydrvmfb
from pydrvmfb_basic import pydrvmfb_basic as pydrvmfb_basic 
from pydrvmfb import pydrvmfb
from pydrvmfb_0x50tmp import pydrvmfb_0x50tmp as pydrvmfb_0x50
from pymfbmultictrl import pymfbmultictrl
from pyrealtime import pyrealtime
import getopt
import numpy as np
import time
import pylab
import scipy.io
import scipy.signal
import json
import socket
import numpy
from numpy import *
import select
import re
import random
from fsrinvmodel import invmodel
import os.path
import matplotlib.pyplot as plt
from params import f_avrg
help_message = '''
The help message goes here.
'''
f_init=False

pyfilename=os.path.basename(sys.argv[0])

couple_register=510. # orm
VCC=5. # V
grav_const = 9.81 # N/s^2

if 'right' in pyfilename: # right arm case (enc not flipped) 
	angle_dir = +1 
	f_mode=0
	print 'right case' 
elif 'left' in pyfilename: # left arm case (enc flipped) 
	angle_dir = -1 
	f_mode=1
	print 'left case' 
else: #default  
	angle_dir = +1
	f_mode=0
	print 'default case' 

###################################
udp2key_turning={
	"0":"wgainL",
	"1":"wgainR",
	"2":"stL",
	"3":"endL",
	"4":"stR",
	"5":"endR",
	"6":"phase",
	"7":"none",
	"8":"none"
}
key2udp_turning={
	"wgainL":"0",
	"wgainR":"1",
	"stL":"2",
	"endL":"3",
	"stR":"4",
	"endR":"5",
	"phase":"6",
	"none":"7",
	"none":"8"
}
paramcoef_turning={
	"0":[10./100., 0.],
	"1":[10./100., 0.],
	"2":[2.*pi/100., 0.],
	"3":[2.*pi/100., 0.],
	"4":[2.*pi/100., 0.],
	"5":[2.*pi/100., 0.],
	"6":[4*1./100., 0.5],
	"7":[4./100., 0.],
	"8":[10./100., 0.]

}

global udp2key
global key2udp
global paramcoef

###################################
class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def generatedrivers(freq):
	global f_init
	if f_init==False:
		drivers = {}
	        # low level driver
		rtmodule = pyrealtime(SMP_FREQ=freq)
		timeout = rtmodule.get_smpltime()
		#drvmfb1 = pydrvmfb(host="192.168.200.2", port=10007, testflag=False, RTNET=True, TIMEOUT = timeout)
		#drvmfb2 = pydrvmfb(host="192.168.201.2", port=10008, testflag=False, RTNET=True, TIMEOUT = timeout)
		#drvmfb0 = pydrvmfb(host="192.168.200.2", port=10007, testflag=False, RTNET=True, TIMEOUT = timeout)
		drvmfb0 = pydrvmfb(host="192.168.201.2", port=10008, testflag=False, RTNET=True, TIMEOUT = timeout)
		#drvmfb1 = pydrvmfb_basic(host="192.168.201.2", port=10008, testflag=False, RTNET=True, TIMEOUT = timeout)
		drvmfb1 = pydrvmfb(host="192.168.203.2", port=10010, testflag=False, RTNET=True, TIMEOUT = timeout)
		drvmfb2 = pydrvmfb(host="192.168.202.2", port=10009, testflag=False, RTNET=True, TIMEOUT = timeout)
		#drvmfb2 = pydrvmfb(host="192.168.202.2", port=10009, testflag=True, RTNET=True, TIMEOUT = timeout)

		drivers["rtmodule"] = rtmodule
		drivers["mfb0"] = drvmfb0
		drivers["mfb1"] = drvmfb1
	        drivers["mfb2"] = drvmfb2
	        #drivers["ctrl"] = mfbctrl = pymfbctrl(drvmfb1, drvmfb2)
		drivers["multictrl"] = mfbmultictrl = pymfbmultictrl()
		drivers["multictrl"].add_mfb(drvmfb0)
		drivers["multictrl"].add_mfb(drvmfb1)
	        drivers["multictrl"].add_mfb(drvmfb2)

		# udp driver 
		host = ''
		port = 9877
		s_rcv =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s_rcv.bind((host,port))
		drivers["s_rcv"] = s_rcv 
		drivers["s_snd"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Slider tuning 
		host = ''
		recv_port = 12002
		s_slider_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s_slider_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)       
		s_slider_recv.bind((host, recv_port))
		drivers["sock_slider_recv"] = s_slider_recv
		drivers["sock_slider_send"] = s_slider_send

		f_init = True
	return drivers

def udprecv(s_rcv, timeout=0.0, defmsg={}):
    ready_to_read, ready_to_write, in_error = select.select([s_rcv], [], [], timeout)
    if ready_to_read:
        for sock in ready_to_read:
            if sock == s_rcv:
                msg_raw=s_rcv.recv(8192)
                defmsg=json.loads(msg_raw)
                print "rcv:", defmsg, "--", msg_raw
                print "time:", time.time()
    else: 
	    pass
	    #print "timeout"
    return defmsg 

def func_epm_inverse_poly31 ( x,p00, p10, p01, p20, p11, p30, p21):
    res = p00 + p10 * x[:,0] + p01 * x[:,1] + p20 * np.power(x[:,0],2) + p11 * x[:,0]*x[:,1] + p30 * np.power(x[:,0],3)+ p21 * np.power(x[:,0],2)*x[:,1]
    return res

def fsr2force(v):
	R2=(couple_register * v)/(VCC-v)		
	f=grav_const*invmodel(R2)/1000. # [N]
	return f

#def main(argv=None, freq=250, exptime=1, drivers=None, stiff=50., f_basic=False ,omega_walk=1.0):
def main(argv=None, freq=200, exptime=1, drivers=None, stiff=50., f_basic=False ,omega_walk=1.0,server_info=None, sound_t=3./2., wgain=5.0, randth=0., f_init_param=True, heel_th=20, vp50comp=10./10., file_simulation="data/test_data_fsrsim.mat"):
	"""
	vp50comp: valve compension value 7bar -- 10./7.
	vp50comp: valve compension value 10bar -- 10./10.
	"""
#def main(argv=None, freq=1000, exptime=2, drivers=None):

	# Get quick and dirty access to socket. 
	global s

	#######Define interior functions for PID control###########
	def calculateProportionalError(reference, measured):
		return reference - measured

	def calculateIntegralError(error, total):
		return total + error

	def calculateDerivativeError(timestep, error, previous_error):
		return (error - previous_error)/float(timestep)

	def PID(reference, measured, total, previous_error, delta):
		"""
		Performs PID control at point in time (t). Requires a value
		corresponding to some reference trajectory, the corresponding
		measured value, the total error from any previous steps, the 
		error from the immediately preceding step, and the timestep
		(for doing a simple one-step derivative calculation).
		"""

		# Gains
		#K_p = 50.0
		#K_i = 0.0
		#K_d = 12.0
		
		## These work well for right heel. 
		K_p = 4.0
		K_i = 0.1
		K_d = 0.3

		# Calculate error terms
		error = calculateProportionalError(reference, measured)
		total_error = calculateIntegralError(error, total)
		derivative = calculateDerivativeError(delta, error, previous_error)

		# Calculate and return control
		control = K_p * error + K_i * total_error + K_d * derivative
		return control, error, total_error	

        #####################################
	global udp2key
	global key2udp
	global paramcoef
	key2udp=key2udp_turning
	udp2key=udp2key_turning
	paramcoef=paramcoef_turning

	#print core.PAMparams
	#asuka########################################
        #sldparam =  scipy.io.loadmat("./param/param.mat") # The original set of parameters
		
	if f_init_param:
		sldparam = scipy.io.loadmat("./param/init_param_kansaiikadai_20160329.mat")
	else:
		sldparam = scipy.io.loadmat("./param/param_kansaiikadai.mat")

	if file_simulation is None:
		pass
	else:
		rslts_sim=scipy.io.loadmat(file_simulation)
	host = 'localhost'
	port = 12003
	serversock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	slider_send_data={}
	for k,v in sldparam.items():
		for k2 in key2udp.keys():
			print k, k2
			if re.match(k,k2):
				slider_send_data[key2udp[k]]=int((v[0,0] - paramcoef[key2udp[k]][1])/paramcoef[key2udp[k]][0])
				
	print "send data:",slider_send_data
	send_msg=json.dumps(slider_send_data)
	serversock.sendto(send_msg, (host, port))
#####################################

	nloop = int(exptime * freq)
	print "omega_walk=%3.3f" % omega_walk
	print "sound_t = %3.3f" %  sound_t
	#omega_walk = 1.0
	sound_t = 1.5
	
	# Load reference trajectories. 'trajectory' is the name of the variable,
	# also saved in the 'trajectory'.mat file. 
	#trajectory = 'tuning_ref_traj'
	trajectory = 'measured_ref_traj'
	
	# Load and form reference trajectory array.
	reference = scipy.io.loadmat(trajectory + '.mat')
	ref_len = len(reference[trajectory])
	
	# Save the reference trajectories. 
	if ref_len < nloop:
		rtraj = np.zeros((nloop,2,3))
	else:
		rtraj = reference[trajectory]
		
	## Create a map from the expected to actual motor indices. This is 
	## necessary due to an error in wiring. Having this motor map means that 
	## if the wiring is fixed or changed it's quick to change this code. This
	## seems to affect only the encoder results and not the input motor values.
	motor_map = numpy.zeros((2,3))
	motor_map[0,0] = 1
	motor_map[0,1] = 0
	motor_map[0,2] = 4
	motor_map[1,0] = 0
	motor_map[1,1] = 1
	motor_map[1,2] = 4
	
	results = {
		"time":numpy.zeros((nloop,1)),
		"angle":numpy.zeros((nloop,1)),
		"angle0":numpy.zeros((nloop,8)),
		"angle1":numpy.zeros((nloop,8)),
		"ad0":numpy.zeros((nloop, 16)),
		"ad1":numpy.zeros((nloop, 16)),
		"ad2":numpy.zeros((nloop, 16)),
		"da0":numpy.zeros((nloop, 8)),
		"da1":numpy.zeros((nloop, 8)),
		"da2":numpy.zeros((nloop, 8)),
		"raw_counter0":numpy.zeros((nloop, 8)),
		"raw_counter1":numpy.zeros((nloop, 8)),
		"raw_counter2":numpy.zeros((nloop, 8)),
		"counter0":numpy.zeros((nloop, 8)),
		"counter1":numpy.zeros((nloop, 8)),
		"idx_counter0":numpy.zeros((nloop, 1)),
		"idx_counter1":numpy.zeros((nloop, 1)),
		"f_sound":numpy.zeros((nloop, 1)),
		"f_noassist":numpy.zeros((nloop, 1)),
		"f_heel":numpy.zeros((nloop, 1)),
		"fsr_force":numpy.zeros((nloop, 4)),
		"fsr_r":numpy.zeros((nloop, 4)),
		"fsr_l":numpy.zeros((nloop, 4)),
		"filt_f":numpy.zeros((nloop, 2)),
		"lc0":numpy.zeros((nloop, 2)),
		"lc1":numpy.zeros((nloop, 2)),
		'y':numpy.zeros((nloop,1)),
		'yd':numpy.zeros((nloop,1)),
		'phi':numpy.zeros((nloop,1)),
		'phi_comp':numpy.zeros((nloop,1)),
		'theta':numpy.zeros((nloop,1)),
		'theta_dot':numpy.zeros((nloop,1)),
		'phase':numpy.zeros((nloop,1)),
		'reference':rtraj,
		'previous_error':numpy.zeros((2,3)),
		'total_error':numpy.zeros((2,3)),
		'delta':1.0/float(freq),
		'nloop':nloop,
		'motor_map':motor_map
		} 
		
	lap=numpy.zeros(nloop)
	print "stiff:", stiff, "[Nm/rad]"
	print "start loop!"
	if drivers==None:
		drivers = generatedrivers(freq)
		drivers["rtmodule"].init_realtime()
	else:
		pass
        parampath = 'poly31_param.mat'
        param = scipy.io.loadmat(parampath)
	p1param = param['p1']
	p2param = param['p2']
	#ENC2RAD = 2. * np.pi/ 16000.
	ENC2RAD = (2.0*np.pi)/float(1.4*3*4000*(676/float(49.0)))
	INIT_COUNTER =2147482368
	f_sound =0
	pre_cycle = cycle = 0
	pre_phase = phase = 0
	w_p1  = w_p2  = omega_walk
	twopiomega = 2 * np.pi * w_p1 
	twopi = 2 * np.pi
	#count_t=-0.004
	INIT_COUNT=-1./freq
	count_t=INIT_COUNT
	INC_COUNT = 1./freq
	f_heel=0
	f_send=0
	delay_t=0
	f_noassist=0
	f_cycle=0
	norder=2
	#cutoff=0.65 #Hz
	cutoff=1.2 #Hz
	B,A=scipy.signal.butter (norder ,cutoff/(freq/2.))
	filtsig_pre = np.array([0,0])
	sig_pre = np.array([0,0])
	#f_avrg =array([ 10.04502744,  34.04567644])

	ret=drivers["rtmodule"].wait()
	omega = 1./1.3 # T = 1.3 
	phasecomp = 0.25 /1.3 * 2*np.pi
	theta= -0.3/1.3 # Diff of RvsL FSR phase and heel-strike walking phase
	#theta= -2.9/1.3 # Diff of RvsL FSR phase and heel-strike walking phase

	dummy_data=scipy.io.loadmat("./data/test_data_noda_01.mat")

	phase_start=0
	st_ct=0
	init_w=750
	init_T=500
	# main loop
	for loop_ct in range(nloop):
		ret=drivers["rtmodule"].wait()

		drivers["mfb0"].realvalue['IO_out'][0]=0xFF
		drivers["mfb1"].realvalue['IO_out'][0]=0xFF

		if phase_start==0:
			ready_to_read, ready_to_write, in_error = select.select([sys.stdin], [], [], 0)
			if ready_to_read:
                        	phase_start=1
				st_ct=loop_ct
				print "start"
			rcv_msg=udprecv(drivers["s_rcv"], timeout=0.0)
			if rcv_msg:
				phase_start=1
				st_ct=loop_ct
				print "start"

		if ret[0] != 0:
			print "error: ret=%3.3f, overrun! %d" % (ret[0],loop_ct)
		#if loop_ct==0:
		#	drivers["mfb1"].realvalue['IO_out'][0]=1
		#if loop_ct==250:
		#	drivers["mfb1"].realvalue['IO_out'][0]=0

		msg = udprecv(drivers['s_rcv'])

		#tera##################################### 
		if "e" in msg.keys():
			print "break"
			break


		# slider value implementation
		ready_to_read, ready_to_write, in_error = select.select([drivers["sock_slider_recv"]], [], [], 0)
		if ready_to_read:
			for sock in ready_to_read:
				if sock == drivers["sock_slider_recv"]:
					recieved_sldr=drivers["sock_slider_recv"].recv(8192)
					if not recieved_sldr:
						print "closing recv port ..."
						drivers["sock_slider_recv"].close()
				
					sldr = json.loads(recieved_sldr)
					for k, v in sldr.items():
						sldparam[udp2key[k]] = float(v)*paramcoef[k][0] + paramcoef[k][1]
		#tera##################################### 
		#print "param:", sldparam["wgain"], sldparam["phase"], sldparam["speed"]
		#asuka####################################
		wgainR = 4.0#float(sldparam["wgainR"])
		wgainL = 4.0#float(sldparam["wgainL"])
		wgainK = 1.0
		omega_walk = float(1./sldparam["phase"]) 
		#stL = float(sldparam["stL"])
		#stR = float(sldparam["stR"])
		#endL = float(sldparam["endL"])
		#endR = float(sldparam["endR"])

		stL = 2* np.pi *( 12.222/100.)
		stR = 2* np.pi*( 13.333/100.)
		#stR = 2* np.pi*( 5.33/100.)
		endL = 2*np.pi*( 46.666/100.)
		endR = 2*np.pi *(55.555/100.)
		dutyL=(endL-stL)/(2.0*pi)
		dutyR=(endR-stR)/(2.0*pi)

		stK1 = 2* np.pi*( 21./100.)
		endK1 = 2*np.pi*( 46.666/100.)
		stK2 = 2* np.pi*( 70./100.)
		endK2 = 2*np.pi*( 88.8/100.)
		dutyK1=(endK1-stK1)/(2.0*pi)
		dutyK2=(endK2-stK2)/(2.0*pi)

		#print dutyL
		#print dutyR
		#results['time'][:loop_ct,:]= lap[loop_ct] = drivers["rtmodule"].readtime()
		lap[loop_ct] = drivers["rtmodule"].readtime()
		results['time'][loop_ct,:]= time.time()
		now = t= results['time'][loop_ct,0] -results['time'][0,0]
		drivers["multictrl"].get_prepare()
		drivers["multictrl"].get()

		results['ad0'][loop_ct,0:16] = drivers["mfb0"].realvalue['ad'][0:16]
		#results['raw_counter0'][loop_ct,:]= np.left_shift(drivers['mfb0'].value['counter'],8).astype(np.int32)/0x100 
		results['raw_counter0'][loop_ct,:]= np.left_shift(drivers['mfb0'].value['counter'],8).astype(np.int32)/0x100# - 0x010000
		rcwt  =results['raw_counter0'][loop_ct,:]
		results['angle0'][loop_ct,:] = rcwt*ENC2RAD
		results['lc0'][loop_ct,0] = (results['ad0'][loop_ct,8]-(-0.0345))*50
		results['lc0'][loop_ct,1] =(results['ad0'][loop_ct,9]-0.0096)*50
		# Todo: ad to pressure conversion should be treated here
		#results['ad0'][loop_ct,0:4] = drivers["mfb0"].realvalue['ad'][0:4]
		results['ad1'][loop_ct,0:16] = drivers["mfb1"].realvalue['ad'][0:16]
		#results['raw_counter1'][loop_ct,:]= np.left_shift(drivers['mfb1'].value['counter'],8).astype(np.int32)/0x100 		
		results['raw_counter1'][loop_ct,:]= np.left_shift(drivers['mfb1'].value['counter'],8).astype(np.int32)/0x100# - 0x010000
		rcwt  =results['raw_counter1'][loop_ct,:]
		results['angle1'][loop_ct,:] = rcwt*ENC2RAD

		results['lc1'][loop_ct,0] = (results['ad1'][loop_ct,8]-(-0.0345))*50
		results['lc1'][loop_ct,1] = (results['ad1'][loop_ct,9]-0.0096)*50
		# Todo: ad to pressure conversion should be treated here
		#results['ad1'][loop_ct,0:16] = drivers["mfb1"].realvalue['ad'][0:16]

		results['ad2'][loop_ct,0:16] = drivers["mfb2"].realvalue['ad'][0:16]

		#print results['ad2'][loop_ct,0:16]
		#print "angle0:",results['angle0'][loop_ct,0:4]
		#print "angle1:",results['angle1'][loop_ct,0:4]
		#print "ad0", results['ad0'][loop_ct,0:8]
		#print "ad1:", results['ad1'][loop_ct,0:8]
		#print "ad2:",results['ad2'][loop_ct,:]
		if f_mode==0:
			angle = results['angle0'][loop_ct,0]
			v2 = results['ad0'][loop_ct,0:4]
			heel_force = results['ad0'][loop_ct,0]
		else:
			angle = results['angle1'][loop_ct,0]
			v2 = results['ad1'][loop_ct,0:4]		
			heel_force = results['ad1'][loop_ct,0]
			#print angle


		results["fsr_force"][loop_ct,:] = fsr_force =  fsr2force(v2)
		
		#if file_simulation is None:
			
		#results["fsr_r"][loop_ct,:] = dummy_data["fsr_r"][loop_ct,:] 
		results["fsr_r"][loop_ct,:] = fsr2force(results["ad0"][loop_ct,8:12])
		#print results["fsr_r"][loop_ct,:]
		#results["fsr_l"][loop_ct,:] = dummy_data["fsr_l"][loop_ct,:] 
		results["fsr_l"][loop_ct,:] = fsr2force(results["ad1"][loop_ct,8:12])
		results["fsr_l"][loop_ct,1] = results["fsr_l"][loop_ct,1]+8.
		#print results["fsr_l"][loop_ct,:]


		drivers["mfb2"].realvalue['da'][1] = results['da2'][loop_ct,1] = -2*(results['angle0'][loop_ct,0]-1.85)/2.0
		drivers["mfb2"].realvalue['da'][4] = results['da2'][loop_ct,4] = 2*(results['angle1'][loop_ct,1]+1.8)/2.0
		#print drivers["mfb2"].realvalue['da'][1]
		#print drivers["mfb2"].realvalue['da'][4]
		fsr_norm_r = 20.
		fsr_norm_l = 20.
		deadvalue = 3.
		pmax = 0.8 
		pmin = 0.0 
		P2V = 10.0
		#drivers["mfb2"].realvalue['da']
		tmp_r = (results["fsr_r"][loop_ct,numpy.array([0,1]) ] - deadvalue)/fsr_norm_r
		tmp_r[pmax < tmp_r ]=pmax 
		tmp_r[tmp_r < pmin]=pmin 
		#drivers["mfb2"].realvalue['da'][3]= tmp_r[0] *P2V
		#drivers["mfb2"].realvalue['da'][2]= tmp_r[1] *P2V  
		tmp_l = (results["fsr_l"][loop_ct,numpy.array([0,1]) ]- deadvalue)/fsr_norm_l
		tmp_l[pmax < tmp_l ]=pmax 
		tmp_l[tmp_l < pmin]=pmin 
		#drivers["mfb2"].realvalue['da'][7]= tmp_l[0] *P2V
		#drivers["mfb2"].realvalue['da'][5]= tmp_l[1] *P2V
		
		## Set the motor torques using positional PID control. 
		control_signal = numpy.zeros((2,3))
		sidelist = ["angle0","angle1"]
		for side in range(2):
			for motor in range(3):
				control_signal[side,motor], \
				results["previous_error"][side,motor], \
				results["total_error"][side,motor] = \
					PID(results["reference"][loop_ct,side,motor], \
						results[sidelist[side]][loop_ct,motor_map[side,motor]], \
						results["total_error"][side,motor], \
						results["previous_error"][side,motor], \
						results["delta"])
						
		#print "pid", results["reference"][loop_ct,side,motor], \
		#				results["angle1"][loop_ct,motor_map[side,motor]], \
		#				results["total_error"][side,motor], \
		#				results["previous_error"][side,motor], \
		#				results["delta"]
		
		## Control motors using PID control to reference trajectory. 
		#drivers["mfb0"].realvalue['da'][0] = control_signal[0,0]
		#drivers["mfb0"].realvalue['da'][1] = control_signal[0,1]
		#drivers["mfb0"].realvalue['da'][2] = control_signal[0,2]
		drivers["mfb1"].realvalue['da'][0] = control_signal[1,0]
		drivers["mfb1"].realvalue['da'][1] = control_signal[1,1]
		drivers["mfb1"].realvalue['da'][2] = control_signal[1,2]
			
			
		## Truncate the signal if it becomes too large.
		limit = 5.0
		for motor in range(3):
			if drivers["mfb0"].realvalue['da'][motor] > limit:
				drivers["mfb0"].realvalue['da'][motor] = limit
			elif drivers["mfb0"].realvalue['da'][motor] < -limit:
				drivers["mfb0"].realvalue['da'][motor] = -limit
			if drivers["mfb1"].realvalue['da'][motor] > limit:
				drivers["mfb1"].realvalue['da'][motor] = limit
			elif drivers["mfb1"].realvalue['da'][motor] < -limit:
				drivers["mfb1"].realvalue['da'][motor] = -limit

		#print "control signal right ankle", drivers["mfb0"].realvalue['da'][0]
		#print "control signal right knee", drivers["mfb0"].realvalue['da'][1]
		#print "control signal right hip", drivers["mfb0"].realvalue['da'][2]
		#print "control signal left ankle", drivers["mfb1"].realvalue['da'][0]
		#print "control signal left knee", drivers["mfb1"].realvalue['da'][1]
		#print "control signal left hip", drivers["mfb1"].realvalue['da'][2]

		# Send data to real time graphs.
		
		#send_data["time"] = results['time'][loop_ct,0]-results["time"][0,0]
		#send_data["data1"] = (drivers["mfb1"].realvalue['da'][0])
		
		#print "r:",tmp_r
		#print "l:",tmp_l

 		drivers["multictrl"].put_prepare()
		drivers["multictrl"].put()
 		drivers["multictrl"].put_post()

		#senddata = {"time": now, "data1":results['angle'][loop_ct,0],"data2":results['da1'][loop_ct,0],"data3":results['da1'][loop_ct,1],"data4":5.-results['ad1'][loop_ct,12],"data5":results['ad1'][loop_ct,8],"data6":results['ad1'][loop_ct,9],"data7":5.-results['ad1'][loop_ct,13],"data8":5.-results['ad1'][loop_ct,14],"data9":5.-results['ad1'][loop_ct,15], "sound":f_sound}
		if f_heel==1:
			if f_send==1:
				f_heel=0
			#print "aft:",f_heel
			
		# Send current time to Matlab PC.
		
		string_time = "%.3f" % now
		rknee_angle_time = "%.5f" % results["angle0"][loop_ct,4]
			
		temp = string_time + rknee_angle_time
		if loop_ct % 5 == 0:
			s.send(temp[0:12])
	
		#if loop_ct == 0:
		#	s.send('0.000' + temp[3:10])
		#elif loop_ct % 5 == 0:
		#	s.send(temp[0:12])		

		if f_mode==0:
			
			#senddata = {"time": now, "data1":np.rad2deg(results['angle'][loop_ct,0])+20.,"data2":results['da0'][loop_ct,0],"data3":results['da0'][loop_ct,1],"data4":fsr_force[0],"data5":results['ad0'][loop_ct,8],"data6":results['ad1'][loop_ct,9],"data7":fsr_force[1],"data8":fsr_force[2],"data9":fsr_force[3], "sound":f_sound, "data11":f_cycle}
			senddata = {"time": now, "data1":0,"data2":results["angle1"][loop_ct,0],"data3":results['da2'][loop_ct,3],"data4":results["fsr_r"][loop_ct,0],"data5":results['da2'][loop_ct,5],"data6":results['da2'][loop_ct,7],"data7":results["fsr_r"][loop_ct,1],"data8":results["fsr_l"][loop_ct,0],"data9":results["fsr_l"][loop_ct,1], "sound":f_sound, "data11":f_heel, "data12":1}
			#print "%3.3f, %3.3f "% tuple(results['ad0'][loop_ct,8:10])
		else:
			#senddata = {"time": now, "data1":np.rad2deg(results['angle'][loop_ct,0])+20.,"data2":results['da1'][loop_ct,0],"data3":results['da1'][loop_ct,1],"data4":fsr_force[0],"data5":results['ad1'][loop_ct,8],"data6":results['ad1'][loop_ct,9],"data7":fsr_force[1],"data8":fsr_force[2],"data9":fsr_force[3], "sound":f_sound, "data11":f_cycle}
			senddata = {"time": now, "data1":results["angle1"][loop_ct,0],"data2":results['da1'][loop_ct,0],"data3":results['da1'][loop_ct,1],"data4":results["angle1"][loop_ct,0],"data5":results['ad1'][loop_ct,8],"data6":results['ad1'][loop_ct,9],"data7":results["fsr_r"][loop_ct,1],"data8":results["fsr_l"][loop_ct,0],"data9":results["fsr_l"][loop_ct,1], "sound":f_sound, "data11":f_heel, "data12":1}

		#senddata = {"time": now, "data1":1}
		json.dumps(senddata)
		if server_info is None:
			pass
		else:
			if loop_ct%5==0:
				#print "send"
				drivers["s_snd"].sendto(json.dumps(senddata), server_info) 
				if f_send==0:
					f_send=1				
					
	drivers["mfb1"].realvalue['IO_out'][0]=1		
	drivers["mfb1"].realvalue['da'][0:8] = 0.0
	drivers["mfb0"].realvalue['da'][0:8] = 0.0
	#drivers["mfb1"].realvalue['IO_out'][0]=0
	# output 
	drivers["multictrl"].put_prepare()
	drivers["multictrl"].put()
	drivers["multictrl"].put_post()

	for i in xrange(250):
		drivers["rtmodule"].wait()		
	drivers["mfb1"].realvalue['IO_out'][0]=0
	drivers["multictrl"].put_prepare()
	drivers["multictrl"].put()
	drivers["multictrl"].put_post()

	samplingtime = results['time'][:,:] - results['time'][0,:] 
	
	print "end loop"
	return results, drivers, samplingtime, sldparam

if __name__ == "__main__":

	# Try connecting to Matlab on my Windows PC. 
	serverIp = '133.186.111.28'
	tcpPort = 10003
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((serverIp, tcpPort))
	time.sleep(1)

	argv = sys.argv
	f_basic =True
	exptime = 2.
	addr_server = None
	port_server = 10003
	filename = "test_data.mat"	
	omega_walk = 1.0
	sound_t = 3./2.
	wgain=5.0
	randth=0.
	f_init_param=True
	heel_th=20

	try:
		try:
			opts, args = getopt.getopt(argv[1:], "ho:bf:t:s:p:w:d:g:r:il:", ["help", "output=", "basic", "filename=","exptime=", "server=","port=", "omega=", "sound_t=", "wgain=", "randth=", "f_init_param", "heel_th="])
		except getopt.error, msg:
			raise Usage(msg)
		flag_expresso = False
		# option processing
		f_basic = False
		for option, value in opts:
			if option == "-v":
                            verbose = True
			if option in ("-h", "--help"):
                            raise Usage(help_message)
			if option in ("-o", "--output"):
                            output = value
			if option in ("-b", "--basic"):
				f_basic = True
				output = value
			if option in ("-f", "--filename"):
				filename= value
			if option in ("-t", "--exptime"):
				exptime = float(value)
			if option in ("-s", "--server"):
				addr_server=value
			if option in ("-p", "--port"):
				port_server=int(value)
			if option in ("-w", "--omega"):
				omega_walk=float(value)
			if option in ("-d", "--sound_t"):
				sound_t=float(value)
			if option in ("-g", "--wgain"):
				wgain=float(value)
			if option in ("-r", "--randth"):
				randth=float(value)
			if option in ("-i", "--f_init_param"):
				f_init_param=False
			if option in ("-l", "--heel_th"):
				heel_th=float(value)

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		sys.exit(2)
	wgain = 5.0
	if addr_server is None: 
		print "noserver"
		rslts, drivers, st, sldparam = main(f_basic=f_basic, exptime=exptime, omega_walk=omega_walk, sound_t=sound_t, wgain=wgain, randth=randth)
	else:
		print "server"
		rslts, drivers, st, sldparam = main(f_basic=f_basic, exptime=exptime, server_info=(addr_server,port_server), omega_walk=omega_walk, sound_t=sound_t, wgain=wgain, randth=randth, f_init_param=f_init_param, heel_th=heel_th)

	savepath = "data/%s"%filename
	print "saving results as ", savepath
	print "saving ..."
	#scipy.io.savemat("data/test.mat",rslts)
	scipy.io.savemat(savepath, rslts)
	#asuka###################################
	scipy.io.savemat("param/param_kansaiikadai.mat",sldparam)
	print "done."

	print "f_avrg=np.array([", np.array([rslts["fsr_r"][:,0:2].sum(axis=1).mean(),rslts["fsr_l"][:,0:2].sum(axis=1).mean()]), "])"
	print "f_avrg=np.array([%f,%f,%f,%f" % tuple(np.array([rslts["fsr_r"][:,0].mean(), rslts["fsr_r"][:,1].mean(),rslts["fsr_l"][:,0].mean(),rslts["fsr_l"][:,1].mean()])), "])"

	#plt.figure()
	#plt.plot(rslts['da1'][:,0], label="p1")
	#plt.plot(rslts['da1'][:,1], label="p2")
	#plt.legend(loc=0)
	#plt.plot(rslts['ad0'][:,4], label="ch1")
    #    plt.plot(rslts['ad0'][:,5], label="ch2")
    #    plt.legend(loc=0)
	
	# Create figure and subplot for later use. 
	#plt.xlabel('Frame number')
	#plt.ylabel('Encoder value')
	#plt.title('Measured vs reference trajectories.')
	
	# row and column sharing
	f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, sharex='col')
	ax1.set_ylim([-0.6,0.4])
	ax1.set_title('left heel')
	ax2.set_ylim([-1.8,0.2])
	ax2.set_title('left knee')
	ax3.set_ylim([-1.28,1.28])
	ax3.set_title('left hip')
	ax4.set_ylim([-0.2,0.3])
	ax4.set_title('right heel')
	ax5.set_ylim([-0.2,2.0])
	ax5.set_title('right knee')
	ax6.set_ylim([-1.4,1.3])
	ax6.set_title('right hip')
	
	ax1.plot(rslts["reference"][1:rslts["nloop"],1,0])
	ax1.plot(rslts["angle1"][1:rslts["nloop"],rslts["motor_map"][1,0]])
	ax2.plot(rslts["reference"][1:rslts["nloop"],1,1])
	ax2.plot(rslts["angle1"][1:rslts["nloop"],rslts["motor_map"][1,1]])
	ax3.plot(rslts["reference"][1:rslts["nloop"],1,2])
	ax3.plot(rslts["angle1"][1:rslts["nloop"],rslts["motor_map"][1,2]])
	ax4.plot(rslts["reference"][1:rslts["nloop"],0,0])
	ax4.plot(rslts["angle0"][1:rslts["nloop"],rslts["motor_map"][0,0]])
	ax5.plot(rslts["reference"][1:rslts["nloop"],0,1])
	ax5.plot(rslts["angle0"][1:rslts["nloop"],rslts["motor_map"][0,1]])
	ax6.plot(rslts["reference"][1:rslts["nloop"],0,2])
	ax6.plot(rslts["angle0"][1:rslts["nloop"],rslts["motor_map"][0,2]])
	plt.get_current_fig_manager().window.showMaximized()
	#figManager = plt.get_current_fig_manager()
	#figManager.window.showMaximized()
	plt.show()
	
	# End connection to Windows PC. 
	s.close()
	
	#sys.exit()
