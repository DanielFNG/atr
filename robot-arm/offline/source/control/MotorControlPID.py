#!/usr/bin/env python
# encoding: utf-8
"""
LoggerTemplate.py

Created by Tomoyuki Noda on 2013-08-05.
Copyright (c) 2013 . All rights reserved.

This is the template for logging data
"""

import sys
#from DrvEMG import DrvEMG
from pydrvmfb import pydrvmfb
from pydrvmfb_basic import pydrvmfb_basic 
from pymfbmultictrl import pymfbmultictrl
from pyrealtime import pyrealtime
import getopt
import numpy as np
import numpy
import time
import pylab
import scipy.io
import pyqtgraph as pg

help_message = '''
The help message goes here.
'''
f_init=False

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def setupPlot(title):
	# Set up graphics window.
	win = pg.GraphicsWindow()
	win.setWindowTitle(title)

	# Add plot and return it. Also return a reference to win, otherwise it goes out of scope
	# and gets deleted.
	plot_window = win.addPlot()
	return plot_window, win

def drawReferenceTrajectory(plot_window, reference_trajectory, size=300, delay=5):
	# Draw the reference trajectory, and create an empty array/curve for
	# the realtime data.
	reference_data = reference_trajectory[:size]
	reference_curve = plot_window.plot(reference_data)
	realtime_data = np.zeros(0)
	realtime_curve = plot_window.plot(realtime_data, pen=(255,0,0)) # red by default
	pg.QtGui.QApplication.processEvents()

	# Pause for effect.
	time.sleep(delay)

	# Return the data and curves
	return reference_data, reference_curve, realtime_data, realtime_curve

def drawRealTime(point, plot_window, reference_trajectory,
				 reference_data, reference_curve,
				 realtime_data, realtime_curve,
				 x_offset, index, size=300):

	if index >= (size/2) and index < len(reference_trajectory) - (size/2):
		# Shift the reference data to the left.
		reference_data[:-1] = reference_data[1:]
		reference_data[-1] = reference_trajectory[size + x_offset]

		# Increment the horizontal offset.
		x_offset += 1

		# Replot the reference trajectory.
		reference_curve.setData(reference_data)
		reference_curve.setPos(x_offset, 0)

		# Shift the realtime data to the left.
		realtime_data[:-1] = realtime_data[1:]
		realtime_data[-1] = point
		#if index >= 300:
		#	realtime_data[-1] = reference_trajectory[index]
		#else:
		#	realtime_data[-1] = reference_trajectory[size/2 - 1]
	else:
		# Append the latest result to the realtime data array.
		realtime_data = np.append(realtime_data, point)

	# Replot the realtime curve.
	realtime_curve.setData(realtime_data)
	realtime_curve.setPos(x_offset, 0)

	# Push these changes on to the graph display.
	pg.QtGui.QApplication.processEvents()

	# Return updated references.
	return reference_data, reference_curve, realtime_data, realtime_curve, x_offset

def calculateProportionalError(reference, measured):
	return reference - measured

def calculateIntegralError(error, total):
	return total + error

def calculateDerivativeError(timestep, error, previous_error):
	return (error - previous_error)/timestep

def PID(reference, measured, total, previous_error, delta):
	'''
	Performs PID control at point in time (t). Requires a value
	corresponding to some reference trajectory, the corresponding measured
	value, the total error from any previous steps, the error from the
	immediately preceding step, and the timestep (for doing a simple one-step
	derivative calculation)
	'''

	# Gains
	# Default gain settings matched to a stationary reference trajectory: Kp = 5.73, Ki = 0.5, Kd = 0.4.
	K_p = 5.73
	K_i = 0.5
	K_d = 0.4
	# Calculate error terms
	error = calculateProportionalError(reference, measured)
	total_error = calculateIntegralError(error, total)
	derivative = calculateDerivativeError(delta, error, previous_error)

	# Calculate and return control control
	control = K_p * error + K_i * total_error + K_d * derivative
	return control, error, total_error

def generatedrivers(freq,f_basic=False,f_rtnet=True):
	global f_init

	if f_init==False:
		drivers = {}
	        # low level driver
		rtmodule = pyrealtime(SMP_FREQ=freq,f_xenomai=False)
		timeout = rtmodule.get_smpltime()
                #drvmfb1 = pydrvmfb_basic(host="192.168.201.2", port=10007, testflag=False, RTNET=True, TIMEOUT = timeout)
                drvmfb1 = pydrvmfb(host="192.168.200.2", port=10007, testflag=False, RTNET=False, TIMEOUT = timeout)
		#drvmfb2 = pydrvmfb(host="192.168.201.2", port=10008, testflag=False, RTNET=True, TIMEOUT = timeout)
		drivers["rtmodule"] = rtmodule
		drivers["mfb1"] = drvmfb1
	        #drivers["mfb2"] = drvmfb2
	        #drivers["ctrl"] = mfbctrl = pymfbctrl(drvmfb1, drvmfb2)
		drivers["multictrl"] = mfbmultictrl = pymfbmultictrl()
		drivers["multictrl"].add_mfb(drvmfb1)
	        #drivers["multictrl"].add_mfb(drvmfb2)
		f_init = True
	return drivers


#def main(argv=None, freq=100, exptime=2, drivers=None, f_basic=False):
def main(argv=None, freq=100, exptime=15, drivers=None, f_basic=False, f_rtnet =False ):
#def main(argv=None, freq=1000, exptime=2, drivers=None):

	nloop = exptime * freq

 	# Initialise total error and previous error to 0 (for PID control).
	total_error = 0
	previous_error = 0

	# Load reference trajectory.
	reference = scipy.io.loadmat('reference/generated_ref_traj.mat')
	reference_trajectory = reference['reference/generated_ref_traj']

	# Step-change constant reference trajectory for tuning gains.
	#reference = scipy.io.loadmat('data/tuning_ref_traj.mat')
	#reference_trajectory = reference['data/tuning_ref_traj']

	# Set up graphics display window.
	plot_window, win = setupPlot("Measured vs. reference trajectory")

	# Draw reference trajectory + setup realtime.
	reference_data, reference_curve, realtime_data, realtime_curve = \
		drawReferenceTrajectory(plot_window, reference_trajectory[:,0])

	# Initialise x_offset to 0 so graph starts at origin.
	x_offset = 0

	if f_basic==True:
		results = {
			"time":numpy.zeros((nloop,1)),
			"ad1":numpy.zeros((nloop, 8)),
			#"ad2":numpy.zeros((nloop, 8)),
			"da1":numpy.zeros((nloop, 4)),
			"raw_counter1":numpy.zeros((nloop, 1)),
			"counter1":numpy.zeros((nloop, 1)),
			}
		lap=numpy.zeros(nloop)
	else:
		results = {
			"time":numpy.zeros((nloop,1)),
			"ad1":numpy.zeros((nloop, 16)),
			#"ad2":numpy.zeros((nloop, 16)),
			"da1":numpy.zeros((nloop, 8)),
			"raw_counter1":numpy.zeros((nloop, 8)),
			"counter1":numpy.zeros((nloop, 8)),
			}
		lap=numpy.zeros(nloop)


	print "start loop!"

	if drivers==None:
		drivers = generatedrivers(freq, f_basic=f_basic,f_rtnet=f_rtnet)
                #if f_rtnet:
                drivers["rtmodule"].init_realtime()
	else:
		pass

	for loop_ct in range(nloop):
		drivers["rtmodule"].wait()
		#results['time'][:loop_ct,:]= lap[loop_ct] = drivers["rtmodule"].readtime()
		lap[loop_ct] = drivers["rtmodule"].readtime()
		results['time'][loop_ct,:]= time.time()
		drivers["multictrl"].get_prepare()
		drivers["multictrl"].get()
		results['ad1'][loop_ct,:] = drivers["mfb1"].realvalue['ad'][:]
		results['raw_counter1'][loop_ct,:]= np.right_shift(drivers['mfb1'].value['counter'], 8).astype(np.int64)
		#results['ad2'][loop_ct,:] = drivers["mfb2"].realvalue['ad'][0:16]

		# Convert the output of the encoder in to radians, and normalise
		# compared to its initial value.
		encoder_value = (2.0*np.pi)/220092*(results['raw_counter1'][loop_ct,0] - results['raw_counter1'][0,0])

		# Draw the realtime plot.
		reference_data, reference_curve, realtime_data, realtime_curve, x_offset = \
			drawRealTime(encoder_value, plot_window, reference_trajectory,
					 reference_data, reference_curve,
					 realtime_data, realtime_curve,
					 x_offset, loop_ct, size=300)

		# Don't actuate the pneumatic actuators.
		drivers["mfb1"].realvalue['da'][0] = 0.0
		drivers["mfb1"].realvalue['da'][1] = 0.0

		# Use PID to control motor.
		drivers["mfb1"].realvalue['da'][2], previous_error, total_error = PID(reference_trajectory[loop_ct,0], encoder_value, total_error, previous_error, 1.0/freq)
		drivers["mfb1"].realvalue['da'][2] = -drivers["mfb1"].realvalue['da'][2]

		# Truncate the signal if it becomes too large.

		limit = 5.0

		if drivers["mfb1"].realvalue['da'][2] > limit:
			drivers["mfb1"].realvalue['da'][2] = limit
		elif drivers["mfb1"].realvalue['da'][2] < -limit:
			drivers["mfb1"].realvalue['da'][2] = -limit

		# Print the motor command for reference.
		print drivers["mfb1"].realvalue['da'][2]

		# Stop execution if the motor output gets too big.
		if drivers["mfb1"].realvalue['da'][2] > 5.0 or drivers["mfb1"].realvalue['da'][2] < -5.0:
			pass
			#sys.exit("Motor command too high.")

 		if loop_ct > 100:
			drivers["mfb1"].realvalue['IO_out'][0]=0

		results['ad1'][loop_ct,:] = drivers["mfb1"].realvalue['ad'][0:16]
		results['da1'][loop_ct,:] = drivers["mfb1"].realvalue['da'][0:8]
        	print "loopct =%d, ad = %3.4f" % (loop_ct, results['ad1'][loop_ct,8])
		if loop_ct % freq == 0:
			print "."
		# output
 		drivers["multictrl"].put_prepare()
		drivers["multictrl"].put()
 		drivers["multictrl"].put_post()

	# Reset some values.
	drivers["mfb1"].realvalue['da'][0:8] = 0.0
	drivers["mfb1"].realvalue['IO_out'][0]=0

	# output
	drivers["multictrl"].put_prepare()
	drivers["multictrl"].put()
	drivers["multictrl"].put_post()


	samplingtime = results['time'][:,:] - results['time'][0,:]

	print "end loop"
	return results,drivers,samplingtime

if __name__ == "__main__":

	argv = sys.argv
	f_basic =False
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "ho:b", ["help", "output=", "basic"])
		except getopt.error, msg:
			raise Usage(msg)
		flag_expresso = False
		# option processing
		for option, value in opts:
			if option == "-v":
                            verbose = True
			if option in ("-h", "--help"):
                            raise Usage(help_message)
			if option in ("-o", "--output"):
                            output = value
			if option in ("-b", "--basic"):
                            f_basic=True
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		sys.exit(2)
	rslts, drivers, st = main(f_basic=f_basic)

	print "-----------------"
	print " to do experiment again"
	print "	> rslts, drivers, st = main(f_basic=f_basic)"
	print " ------------------"


	#figure()
	#plot(numpy.diff(st[:,0]))
	#title("lap")
	#xlabel("sampling")
	#ylabel("diff time[sec]")
	#ylim([0.001980,0.002020])

	savepath = "data/test_pid.mat"
	print "saving results as ", savepath
	print "saving ..."
	scipy.io.savemat(savepath,rslts)
	print "done."
	#sys.exit()
