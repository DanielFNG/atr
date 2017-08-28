### Data naming/storage convention

It is assumed that data files are saved in the following form: [PREFIX '_thigh=' VALUE_thigh '_shank=' VALUE_shank '.mat']. 

PREFIX is just some descriptive prefix, while the other variables are values for the thigh and shank cuff positions.

Such a convention allows for batch processing of data which is useful for analysis of results. By default it will be assumed that all data
files are in the data folder, however an alternate folder (e.g. data/this_data) will be supported as an optional argument to analysis 
functions. It will also be possible to specify SHANK_ONLY or THIGH_ONLY keywords for data coming from 1D experiments. 
