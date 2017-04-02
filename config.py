"""

custom settings file
CLOSE PROGRAM AFTER CHANGING SETTINGS FOR UPDATING

"""

Experiment_Directory = r"D:\DATA\master2016\Samples\32\pdata\1"			# The default experiment location
Database_Directory = r"D:\DATA\master2016\DATABASE"				# Compile the database with this data; the db is also stored here

#parameters
	#plots
plot_exp = True					# will plot each chunk next to each other to show which chunks are noisy
plot_chunk = True					# plot the chunk with its determined sacharide in the database
plot_values = True					# will plot each chunk on different plot with ppm's given to each curve
plot_integration = True				# should only be used for debugging purpoces

plot_diagonal = True				# should the threshold be determined using plot or use default value?

	#Alternate methods
am_norm = False
am_int = False



	#General parameters
gp_chunks = False					# on False by default; if you set to true; the user will be prompted
gp_print = 3						# the default amount of sacharides returned
gp_threshold = 0.2					# default threshold for the diagonal peaks in the 3d experiment
gp_duplet_filtering = True

