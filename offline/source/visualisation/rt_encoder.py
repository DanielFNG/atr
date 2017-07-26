import pyqtgraph as pg
import numpy as np
import scipy.io
import time

# This was test code for implementing pyqtgraph for plotting the encoder position of the 1DOF arm vs the reference.
# The rtgraph.py code is an example code from the developers of pyqtgraph, on which this code was based. Elements of
# this script are in the MotorControlPID.py script.

# Set up graphics window.
win = pg.GraphicsWindow()
win.setWindowTitle('Testing real-time tracking.')

# Load reference trajectory.
reference = scipy.io.loadmat('reference/generated_ref_traj.mat')
reference_trajectory = reference['generated_ref_traj']

# Add plot to graphics window.
plot_window = win.addPlot()

# Horizontal size of the plot window.
hsize = 300

# Draw the reference trajectory, and create an empty array/curve for the realtime data.
reference_data = reference_trajectory[:hsize,0]
realtime_data = np.zeros(0)
reference_curve = plot_window.plot(reference_data)
realtime_curve = plot_window.plot(realtime_data, pen=(255,0,0))

# Graph horizontal offset, starts at 0 i.e. the origin.
x_offset = 0

# Process commands using pyqtgraph.
pg.QtGui.QApplication.processEvents()

# 5 second delay before experiment starts.
time.sleep(5)

def update(index):
    global realtime_data, x_offset

    if index >= 150 and index < 2850:
        # Shift the reference data to the left.
        reference_data[:-1] = reference_data[1:]
        reference_data[-1] = reference_trajectory[hsize + x_offset]

        # Increment the horizontal offset.
        x_offset += 1

        # Replot the reference trajectory.
        reference_curve.setData(reference_data)
        reference_curve.setPos(x_offset, 0)

        # Shift the realtime data to the left.
        realtime_data[:-1] = realtime_data[1:]
        if index >= 300:
            realtime_data[-1] = reference_trajectory[index]
        else:
            realtime_data[-1] = reference_trajectory[149]
    else:
        # Append the latest result to the realtime data array.
        realtime_data = np.append(realtime_data,reference_trajectory[index])

    # Replot the realtime curve.
    realtime_curve.setData(realtime_data)
    realtime_curve.setPos(x_offset, 0)

    # Push these changes on to the graph display.
    pg.QtGui.QApplication.processEvents()

# Control loop.
for i in range(3000):
    update(i)

# A final wait at the end of the experiment.
time.sleep(5)