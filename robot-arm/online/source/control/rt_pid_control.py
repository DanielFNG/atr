#!/usr/bin/env python
# encoding: utf-8
"""
rt_pid_control

Modified from pymfbtrqctrl_sample_core_for_windows_gui.py
by Daniel Gordon on 2017-7-21.

pymfbtrqctrl_sample_core_for_windows_gui

Created by Tatsuya Teramae on 2015-9-18
Copyright (c) 2015 . All rights reserved.
"""

import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../../pyxorcore")
sys.path.append("../../../pycalib")
sys.path.append("../../../pydrivers")
import time
import select
import scipy
import matplotlib.pyplot as plt
import scipy.io
import numpy as np
import simplejson as json
from pydrvmfb import pydrvmfb
import socket
import re
# import classes
import pymfbcore_for_windows_gui as pymfbcore # drivers and configures class
import pymfbio_core_for_windows_gui as pymfbio_core # I/O loop class
import pymfbtrqctrl_calib_core as jcalib # calibration class
import valvecalib_ankle_knee2 as vcalib # parameter fitting class
import pymfbtrqctrl_basic_xeno as trqctrl
from DrvMFBValveCalib import DrvValveCalib 
import onedofcalib # measurement of calibration data class
help_message = '''
This program measure haptics sensor data and send data to viewer PC
'''

V2LCa = np.array([445.7136,400.0])
LC_bias = np.array([-23.5,-19.5])
RAD2DEG = (180./np.pi)

def AddDrivers(core): # Addition of drivers
	pass

def AddConfig(core, key, data_type, conffilepath): # Addition of configure terms
    core.read_config(core.config, conffilepath = conffilepath) # reload configure file
    if data_type=="int":
        core.config[key] = int(core.conf.get("param", key))
    elif data_type=="bool":
        core.config[key] = core.conf.getboolean("param", key)
    elif data_type=="float":
        core.config[key] = float(core.conf.get("param", key))
    elif data_type=="list-int":
        core.config[key] = map(int, list(core.conf.get("param", key).split(",")))
    elif data_type=="list-float":
        core.config[key] = map(float, list(core.conf.get("param", key).split(",")))
    else:
        core.config[key] = core.conf.get("param", key)


def DisplayFormat(results, key, data_key, j, ch):
        print key,"=",results[data_key][j, ch]

def AddResults(core): # Addition of keys
	nloop = int(core.config["exp_time"]*core.config["freq_ctrl"]+0.5)
	core.results["tr"] = np.zeros((nloop,2))
	core.results["agnles_index_calib"] = np.zeros((nloop,10))
	core.results["counter_with_zero_mfb1"] = np.zeros((nloop,8))
	core.results["err"] = np.zeros((nloop,1))

	# Load reference trajectory. 'trajectory' is name of variable, also saved in 'trajectory'.mat file.
	# Choose reference trajectory.  
	trajectory = 'generated_ref_traj'
	#trajectory = 'tuning_ref_traj'

	# Load and form reference trajectory array.
	reference = scipy.io.loadmat(trajectory + '.mat')
	ref_len = len(reference[trajectory])
	if ref_len < nloop:
		core.results["reference"] = np.zeros((nloop,1))
		core.results["reference"][0:ref_len] = reference[trajectory]
	else:
		core.results["reference"] = reference[trajectory]

	# Terms for use in PID controller.
	core.results["previous_error"] = 0
	core.results["total_error"] = 0
	core.results["delta"] = 15.0/200.0 # made a mistake with delta calculation, gains are set up for this value of exp time/freq. 
	core.results["nloop"] = nloop	   # probably won't work as well if you change these values!! would have to retune, but it's not 
									   # a priority 
	

def Display(results, j):
	pass

def mykeyinterrupt(line):
	if line == "e\n":
		print "break"

		sys.exit()
	else:
		pass

# ilqg method function
def MyFunc(core, results, send_data, offlinedata, j): # original function

	ready_to_read, ready_to_write, in_error = select.select([sys.stdin], [], [], 0)

	# Define some functions for doing PID control. 
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
#		K_p = 10.0
#		K_i = 0.7
#		K_d = 12.0
		K_p = 50.0
		K_i = 0.0
		K_d = 12.0
		#K_p = 0.0
		#K_i = 0.0
		#K_d = 0.0

		# Calculate error terms
		error = calculateProportionalError(reference, measured)
		total_error = calculateIntegralError(error, total)
		derivative = calculateDerivativeError(delta, error, previous_error)

		# Calculate and return control
		control = K_p * error + K_i * total_error + K_d * derivative
		return control, error, total_error

	# initialize DA value
	setvalue_mfb1=[0,0,0,0,0,0,0,0] # for mfb1
	setvalue_mfb2=[0,0,0,0,0,0,0,0] # for mfb2

	core.results["counter_with_zero_mfb1"][j,:], core.results["counter_mfb1"][j,:],  core.results["counter_raw_mfb1"][j,:] = onedofcalib.CalcAngleWithZeroPoint(core, mfb="mfb1", counter_raw=core.results["counter_raw_mfb1"][j,:])
	
	# LC V to N
	results['LC'][j,0] = V2LCa[0]*(results["ad_mfb1"][j,3]) - LC_bias[0]
	results['LC'][j,1] = V2LCa[1]*(results["ad_mfb1"][j,4]) - LC_bias[1]	# gravity term in one dgree of freedom

	# Gravity compensation term. 
        gcomp = -0.1*1.7*9.81*np.sin(results["counter_mfb1"][j,0])

	# Convert encoder output to radians, and normalise compared to initial value.
	# Ends up assuming the initial position is 0, while I assume the onedofcali doesn't do this. However, my reference
	# trajectories are set up to do this, so I'll keep it this way for now. 
	core.results["counter_mfb1"][j,0] = (2.0*np.pi)/220092.0 * (results["counter_raw_mfb1"][j,0] - results["counter_raw_mfb1"][0,0])

	# Calculate PID control.
	pid_control, core.results["previous_error"], core.results["total_error"] = PID(core.results["reference"][j,0], core.results["counter_mfb1"][j,0], core.results["total_error"], core.results["previous_error"], core.results["delta"])
	pid_control = -pid_control # fix this

	# Truncate the signal if it becomes too large.
	limit = 5.0
	if pid_control > limit:
		pid_control = limit
	elif pid_control < -limit:
		pid_control = -limit

	# Desired torque as total control input. Not working in torque space at the moment, so only PID.
	dtq = pid_control 
	results['dtq'][j,0] = dtq

	#setvalue_mfb1[2]=dtq/(0.46*23.*2.5*0.0276)
	setvalue_mfb1[2] = dtq # no need for torque -> motor conversion as we are just doing PID

	print "dtq:", dtq, "motor input:", setvalue_mfb1[2], "angle:", results["counter_mfb1"][j,0], "tr:", core.results["reference"][j,0]

	# Won't use send_data for the time being. I'll still send the time just incase it needs something.  

	send_data["time"] = results["times1"][j,0]-results["times1"][0,0]
	send_data["data1"] = (results["counter_mfb1"][j,0])
	send_data["data2"] = (core.results["reference"][j,0]+ 3)
	#send_data["data3"] = np.rad2deg(results["counter_mfb1"][j,0])
	#send_data["data4"] = np.rad2deg(results["counter_mfb1"][j,0])
	#send_data["data5"] = np.rad2deg(results["counter_mfb1"][j,0])
	#send_data["data6"] = np.rad2deg(results["counter_mfb1"][j,0])
	#send_data["data7"] = np.rad2deg(results["counter_mfb1"][j,0])
	#send_data["data8"] = np.rad2deg(results["counter_mfb1"][j,0])
	#send_data["data2"] = np.sin(2*np.pi*2*j/core.config["freq_ctrl"])
	#send_data["data3"] = np.sin(2*np.pi*3*j/core.config["freq_ctrl"])
	#send_data["data4"] = np.sin(2*np.pi*4*j/core.config["freq_ctrl"])
	#send_data["data5"] = np.sin(2*np.pi*5*j/core.config["freq_ctrl"])
	#send_data["data6"] = np.sin(2*np.pi*0.1*j/core.config["freq_ctrl"])
	#send_data["data7"] = np.sin(2*np.pi*0.5*j/core.config["freq_ctrl"])
	#send_data["data8"] = np.sin(2*np.pi*0.2*j/core.config["freq_ctrl"])

	if j % 1250 == 1:
		print ".",
		sys.stdout.flush()
	if j % 4 == 0:
		core.drivers["s_snd"].sendto(json.dumps(send_data), (core.config["snd_ip"], core.config["snd_port"]) )
	if j == core.results["nloop"]-1:
		setvalue_mfb1[2] = 0
	
	return setvalue_mfb1, setvalue_mfb2, results, send_data

def main(core, conffilepath="./default.conf", myfunc=None):

        # Addition of original configure term 
        key="f_Display"
        data_type="bool"
        AddConfig(core, key, data_type, conffilepath)
	AddResults(core)

	results = pymfbio_core.mainloop(core, conffilepath=conffilepath, myfunc=myfunc)

	return results

if __name__ == '__main__':

	# Create figure and subplot for later use. 
	fig = plt.figure('trajectories')
	plt.xlabel('Frame number')
	plt.ylabel('Encoder value')
	plt.title('Measured vs. reference trajectory.')
	plt.grid(True)

        # Default configure file path
	conffilepath="./myconf.conf"

        # Load core control class
	core = pymfbcore.PyMfbXenomaiCore(conffilepath) # MFB core program import

        # Addition of original drivers
        AddDrivers(core)

	# Addition of original results items
	AddResults(core)

	# print "\nstart command example:"
	# print "results = main(core, conffilepath=\"./myconf.conf\", myfunc=MyFunc)"
	# print "please change conffilepath and myfunc to your configure file and control function"

	results = main(core, conffilepath="./myconf.conf", myfunc=MyFunc)
	
	plt.plot(core.results["reference"][0:core.results["nloop"],0])
	plt.plot(core.results["counter_mfb1"][1:core.results["nloop"],0])
	plt.show()

