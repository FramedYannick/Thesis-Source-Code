"""""
designed by Dandois for fitting the curves on the peaks

"""


def func ():
    return ()

def func_H1 (I, m, x1,y1):
    return (m*(I-x1)+y1)

def fn_plot_data (axis, info):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    color = 0
    colors = ['ro', 'bo', 'go', 'co', 'mo', 'yo', 'ko','r^', 'b^', 'g^', 'c^', 'm^', 'y^', 'k^','r*', 'b*', 'g*', 'c*', 'm*', 'y*', 'k*','rd', 'bd', 'gd', 'cd', 'md', 'yd', 'kd','rD', 'bD', 'gD', 'cD', 'mD', 'yD', 'kD',]
    peaks = info[1]+ info[2]

    for y in range(len(peaks)):
        if y == len(colors)-1:
            color = 0
        else:
            color += 1
        ydata = (peaks[y]['data'])
        ppm = peaks[y]['ppm']
        ax.plot(axis, ydata, colors[color],label=str(ppm))
    plt.legend()
    plt.show()

def fn_SSD (listA, listB=[]):
    import numpy as np
    from config import Default_show
    if listB == []:
        for x in range(len(listA)):
            listB.append(0.)
    data = np.array(listA) - np.array(listB)
    result = np.sqrt(np.sum((np.mean(data)-data)**2))
    return result


################################################################################ MAIN FUNCTION
def fn_fit_curves (vclist, peaks_value_list, peaks_ppm, printlabel):
    from GUI_mainframe import update_GUI
    import numpy as np
    from scipy.optimize import curve_fit
    import config

    update_GUI("Fitting curves to the data...",printlabel)

    #normalize the data towards the first
    max = np.max(peaks_value_list)
    for x in range(len(peaks_value_list)):
        for y in range(len(peaks_value_list[x])):
            peaks_value_list[x][y] = peaks_value_list[x][y]/max

    #collect information on each peak
    info = ["",[],[]]
    for x in range(len(peaks_value_list)):
        temp_ppm = peaks_ppm[x]
        temp_decay = peaks_value_list[x]
        # check for the different types of H1s
        if temp_ppm > 4.25 and temp_decay[0] > 0.3:
            temp_max_ind, temp_max = sorted(enumerate(temp_decay),key=(lambda x: x[1]))[len(temp_decay)-1]
            temp_drop = (temp_max - temp_decay[len(temp_decay)-1])
            m = temp_drop / (vclist[temp_max_ind] - vclist[len(temp_decay)-1])
            #calculate linear function
            temp_lin = []
            for I in vclist:
                temp_lin.append(func_H1(I,m,vclist[temp_max_ind],temp_max))
            temp_SSD = fn_SSD(temp_decay,temp_lin)
            temp_info = {'data': temp_decay, 'ppm': temp_ppm, 'duplet': False, 'curve': {'drop': temp_drop,'lin_SSD': temp_SSD, 'rico': m, 'max_mix': (vclist[temp_max_ind], temp_max)}}
            info[1].append(temp_info)

        # collect info on the NON H1 peaks
        elif temp_ppm < 4.25:










            temp_info = {'data': temp_decay, 'ppm': temp_ppm,'duplet': False}
            info[2].append(temp_info)

    #duplet filtering - H1
    remove = []
    for x in range(len(info[1])):
        for y in range(x+1,len(info[1])):
            SSD = fn_SSD(info[1][x]['data'], info[1][y]['data'])
            D_ppm = abs(info[1][y]['ppm']-info[1][x]['ppm'])
            D_drop = abs(info[1][y]['curve']['drop']-info[1][x]['curve']['drop'])
            if SSD < 0.05 and D_ppm < 0.01 and D_drop < 0.10:
                remove.append(y)
                info[1][x]['duplet'] = True
                info[1][y]['duplet'] = True
                info[1][x]['duplet_SSD'] = SSD
                info[1][x]['duplet_DATA'] = info[1][y]
    remove = sorted(remove, reverse=True)
    if config.Default_show:
        print("removing H1-peaks: %s" %str(len(remove)))
    for x in remove:
        info[1].pop(x)

    #duplet filtering - other H
    remove = []
    for x in range(len(info[2])):
        for y in range(x+1,len(info[2])):
            SSD = fn_SSD(info[2][x]['data'], info[2][y]['data'])
            D_ppm = abs(info[2][y]['ppm']-info[2][x]['ppm'])
            if SSD < 0.05 and D_ppm < 0.01:
                remove.append(y)
                info[2][x]['duplet'] = True
                info[2][y]['duplet'] = True
                info[2][x]['duplet_SSD'] = SSD
                info[2][x]['duplet_DATA'] = info[2][y]
    remove = sorted(remove, reverse=True)
    if config.Default_show:
        print("removing non H1-pekas: %s" %str(len(remove)))
    for x in remove:
        info[2].pop(x)



    #plot if enabled in config
    if config.Default_show:
        print("H1 peaks:")
        for x in range(len(info[1])):
            print(info[1][x])
        print("non H1 peaks:")
        for x in range(len(info[2])):
            print(info[2][x])
        fn_plot_data(vclist, info)
    update_GUI("Ready to process all peaks.", printlabel)

    return info,vclist
