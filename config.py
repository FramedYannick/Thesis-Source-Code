"""

custom settings file
to be implemented with future possibility towards exe!
CLOSE PROGRAM AFTER CHANGING SETTINGS FOR UPDATING

"""

Default_Directory = r"D:\DATA\master2016\Test_500\2\pdata\1"
Database_Directory = r"D:\DATA\master2016\DATABASE"	#compile the database with this data

#parameters for peak picking
Default_inter_peak_distance = 0.0005                      #minimum distance between peaks (in ppm)
Default_minpeakhight = 0.01                               #percentage of biggest peak each peak must have to be seen as a peak
Default_show = True                                       #should a plot of the peaks be shown (default = false)
Default_mode = True                                       #True for integrals; false for intensities

#parameters for database comparison
