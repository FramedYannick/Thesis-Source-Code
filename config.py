"""

custom settings file
CLOSE PROGRAM AFTER CHANGING SETTINGS FOR UPDATING

"""

Experiment_Directory = r"D:\DATA\master2016\Samples\32\pdata\1"			# The default experiment location
Database_Directory = r"D:\DATA\master2016\DATABASE"				# Compile the database with this data; the db is also stored here

#parameters
	#plots
plot_exp = False					# will plot each chunk next to each other to show which chunks are noisy
plot_chunk = False					# plot the chunk with its determined sacharide in the database
plot_values = False					# will plot each chunk on different plot with ppm's given to each curve
plot_integration = True				# should only be used for debugging purpoces

	#Alternate methods
am_norm = False
am_int = False



	#General parameters
gp_chunks = False					# on False by default; if you set to true; the user will be prompted
gp_print = 3						# the default amount of sacharides returned


