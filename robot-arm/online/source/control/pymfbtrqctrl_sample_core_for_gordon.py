#!/usr/bin/env python
# encoding: utf-8
"""
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
		
	# initialize DA value
	setvalue_mfb1=[0,0,0,0,0,0,0,0] # for mfb1
	setvalue_mfb2=[0,0,0,0,0,0,0,0] # for mfb2

	core.results["counter_with_zero_mfb1"][j,:], core.results["counter_mfb1"][j,:],  core.results["counter_raw_mfb1"][j,:] = onedofcalib.CalcAngleWithZeroPoint(core, mfb="mfb1", counter_raw=core.results["counter_raw_mfb1"][j,:])
	# LC V to N
	results['LC'][j,0] = V2LCa[0]*(results["ad_mfb1"][j,3]) - LC_bias[0]
	results['LC'][j,1] = V2LCa[1]*(results["ad_mfb1"][j,4]) - LC_bias[1]	# gravity term in one dgree of freedom

        gcomp = -0.1*1.7*9.81*np.sin(results["counter_mfb1"][j,0])
	results["tr"][j,0] = tr = np.deg2rad(10.)*sin(2.*np.pi*0.5*j/250.)
	results["err"][j,0] = err = results["counter_mfb1"][j,0] - tr
	ierr = (results["err"][j,0] - results["err"][j-1,0])/250.

	PI = 15.*err + 0.5*ierr
	# desired torque
	dtq = gcomp + PI
	results['dtq'][j,0] = dtq

	setvalue_mfb1[2]=dtq/(0.46*23.*2.5*0.0276)

	print "dtq:", dtq, "motor input:", setvalue_mfb1[2], "angle:", results["counter_mfb1"][j,0], "tr:", tr

	send_data["time"] = results["times1"][j,0]-results["times1"][0,0]
	send_data["data1"] = np.sin(2*np.pi*1*j/core.config["freq_ctrl"])
	send_data["data2"] = np.sin(2*np.pi*2*j/core.config["freq_ctrl"])
	send_data["data3"] = np.sin(2*np.pi*3*j/core.config["freq_ctrl"])
	send_data["data4"] = np.sin(2*np.pi*4*j/core.config["freq_ctrl"])
	send_data["data5"] = np.sin(2*np.pi*5*j/core.config["freq_ctrl"])
	send_data["data6"] = np.sin(2*np.pi*0.1*j/core.config["freq_ctrl"])
	send_data["data7"] = np.sin(2*np.pi*0.5*j/core.config["freq_ctrl"])
	send_data["data8"] = np.sin(2*np.pi*0.2*j/core.config["freq_ctrl"])

	if j % 1250 == 1:
		print ".",
		sys.stdout.flush()
	if j % 4 == 0:
		core.drivers["s_snd"].sendto(json.dumps(send_data), (core.config["snd_ip"], core.config["snd_port"]) )
	
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
