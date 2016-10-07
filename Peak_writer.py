#Peak writer for xml extraxtion towards processed spectra

def fn_peak_xml (peaks_ppm, dir):   #peaks is list of tuples!!!
    print(dir)
    dir_file = dir + r"\peaklist.xml"
    write = open(dir_file, 'w')
    write.writelines('<?xml version="1.0" encoding="UTF-8"?>\n<PeakList modified="2016-09-26T16:37:16">\n  <PeakList2D>\n    <PeakList2DHeader creator="ind assignment@studentpc4-PC" date="2015-02-19T15:11:12" expNo="4" name="BaPr_minor17" owner="ind assignment" procNo="1" source="C:/data/bach2015/nmr">\n      <PeakPickDetails>\n	</PeakPickDetails>\n    </PeakList2DHeader>')
    for x in peaks_ppm:
        if type(x) == type((1,)):
            if len(x) <3:
                x = x + (123.4,'E',)
            elif len(x)<4:
                x = x + ('E')
        elif type(x) == type([]):
            if len(x) < 3:
                x = x + [123.4, 'E']
            elif len(x) < 4:
                x = x + ['E']
        write.writelines('    <Peak2D F1="%f" F2="%f" annotation="%s" intensity="%f" type="1"/>\n' %(x[0], x[1],x[3],x[2]))
    write.writelines("  </PeakList2D>\n</PeakList>")
    return

def fn_peak_ppm (peaks, SW_pmm, SO1_ppm, data_lenx, data_leny, xcorr_ppm=0, ycorr_ppm=0):
    peaks2 = []
    y = 0
    for x in peaks:
        peaks2.append((((data_lenx-x[0])/data_lenx*SW_pmm)+(SO1_ppm-0.5*SW_pmm),((data_leny-x[1])/data_leny*SW_pmm)+(SO1_ppm-0.5*SW_pmm)))
    return peaks2;


def fn_peaks_ppm_plot_converter (peaks_ppm):
    peaksx = []
    peaksy = []
    for x in peaks_ppm:
        peaksx.append(x[0])
        peaksy.append(x[1])
    return [peaksx, peaksy]

def fn_peak_corrector (peaks, data, B0_hz):         #temp correction till i find actual cause
    xcorr_ppm, ycorr_ppm = 0,0
    #xcorr_ppm = len(data)*-0.0002449
    #ycorr_ppm = len(data[0])*-0.0002449
    """
    import numpy as np
    (x, y) = np.unravel_index(data.argmax(), data.shape)
    (x_p, y_p, a, b, c, d) = sorted(peaks, key=lambda x: x[5], reverse=True)[0]
    print("max intensity x channel: %f and %f" %(data[x][y], d))
    xcorr_ppm = 0 #(x - x_p)/B0_hz
    ycorr_ppm = 0 #(y - y_p)/B0_hz
    print("correction is " + str(xcorr_ppm) + "and" + str(ycorr_ppm))
    """
    return xcorr_ppm, ycorr_ppm

def fn_data_plotter (dir, data, peaks_ppm, SW_ppm, SO1_ppm):
    import matplotlib.pyplot as plt  # for plotting
    import numpy as np
    from config import Default_dpi

    fn_peak_xml(peaks_ppm, dir)
    [peaksx, peaksy] = fn_peaks_ppm_plot_converter(peaks_ppm)

    # create the plot - needs complete makeover!!! - only here for reference; can be deleted :D
    cl = data.std() * 2 * 1.2 ** np.arange(10)  # make list of 10 hights to be drawn
    fig = plt.figure()
    fig.set_size_inches(15, 15)
    ax = fig.add_subplot(111)
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.xaxis.grid(color='gray', linestyle='dashed')
    ax.contour(data, cl, colors='blue', extent=(SO1_ppm + 0.5 * SW_ppm, SO1_ppm - 0.5 * SW_ppm, SO1_ppm + 0.5 * SW_ppm, SO1_ppm - 0.5 * SW_ppm))
    ax.plot(peaksx, peaksy, 'ro', alpha=0.5)
    ax.set_ylabel("1H (ppm)")
    ax.set_xlabel("1H (ppm)")
    plt.gca().invert_xaxis()
    plt.gca().invert_yaxis()
    fig.savefig(dir + r"\pic.png", dpi=Default_dpi)
    return (fig)


def fn_peak_plotter (dir, peaklist):
    import matplotlib.pyplot as plt
    from config import Default_dpi
    fig = plt.figure()
    fig.set_size_inches(15, 15)
    ax = fig.add_subplot(111)
    ax.yaxis.grid(color='gray', linestyle='dashed',which='both')
    ax.xaxis.grid(color='gray', linestyle='dashed',which='both')
    colors = ['ro', 'b^','g^','c^','m*','yx','bd','kD']
    for x in range(len(peaklist)):
        [peaksx, peaksy] = fn_peaks_ppm_plot_converter(peaklist[x])
        ax.plot(peaksx, peaksy, colors[x], alpha=0.5)
    ax.set_ylabel("1H (ppm)")
    ax.set_xlabel("1H (ppm)")
    plt.gca().invert_xaxis()
    plt.gca().invert_yaxis()
    fig.savefig(dir + r"\pic.png", dpi=Default_dpi)
    return (fig)
