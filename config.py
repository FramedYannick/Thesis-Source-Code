"""

custom settings file
to be implemented with future possibility towards exe!
CLOSE PROGRAM AFTER CHANGING SETTINGS FOR UPDATING

"""

Default_Directory = r"D:\DATA\master2016\Sucrose_D2O"

#analysis parameters
Default_Threshold = 0.005                                   #threshhold for peak picking
Default_Picker = "Default"                                  #not implemented yet
Default_dpi = 350                                           #defines max zoom; normal value is 100-120; optimal 200

#processing parameters
Default_Plotting = True                                     #true will create plot inside the proc. directory
Default_Sugar_ARange = [3.8,10]                             #ppm range for alpha-hydrogen - INCORRECT
Default_copy = True                                         #should top half be copied on bottom for missed peaks
															#this is time intensitive; and should not be done with low F2 resolution
Default_artefacts = False                                   #is compensation for artefacts and duplets


#threshholt values
Default_Diag_sep = 0.007                                    #threshhold for distance to diagonal and for dup/triplets
Default_Threshold_sep = 0.02                                #threshhold for peak seperation
