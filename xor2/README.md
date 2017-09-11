### Data naming/storage convention

To reduce clutter in the data folder and allow for batch processing of data, 
certain naming and storage conventions will be adopted. This is only really 
necessary for files which are to be automatically analysed i.e. multiple 
files corresponding to an experiment.

It is assumed that such files are saved in a subdirectory of the ATR/XoR2 'data' 
folder with some name, e.g. 'data/test_2emg'. Then, files should be saved with
a filename of the form ['thigh=' VALUE_thigh '_shank=' VALUE_shank '.mat'].
Decimal points in values should be replaced with hyphens, with the format 
2digit-1digit i.e. 02-5, 10-0, etc. 

If a 2D experiment was carried out e.g. only using the thigh cuff, the value
for the unused parameter should be the string 'NULL'.

Such a convention allows for batch processing of data which is useful for 
analysis of results. 
