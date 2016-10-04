#Peak writer for xml extraxtion towards processed spectra

def fn_peak_xml (peaks_ppm, dir):   #needs proper writing
    dir_file = dir + r"\peaklist.xml"
    write = open(dir_file, 'w')
    write.writelines('<?xml version="1.0" encoding="UTF-8"?>\n<PeakList modified="2016-09-26T16:37:16">\n  <PeakList2D>\n    <PeakList2DHeader creator="ind assignment@studentpc4-PC" date="2015-02-19T15:11:12" expNo="4" name="BaPr_minor17" owner="ind assignment" procNo="1" source="C:/data/bach2015/nmr">\n      <PeakPickDetails>\n	</PeakPickDetails>\n    </PeakList2DHeader>')
    for x in peaks_ppm:
        write.writelines('    <Peak2D F1="%f" F2="%f" annotation="A" intensity="1256" type="1"/>\n' %(x[0], x[1]))
    write.writelines("  </PeakList2D>\n</PeakList>")
    return

def fn_peak_ppm (peaks, SW_pmm, data_len,xcorr_ppm=0, ycorr_ppm=0):
    peaks2 = []
    y = 0
    for x in peaks:
        peaks2.append((((data_len-x[0])/data_len*SW_pmm)+xcorr_ppm,((data_len-x[1])/data_len*SW_pmm)+ycorr_ppm))
    return peaks2;


def fn_peaks_ppm_plot_converter (peaks_ppm):
    peaksx = []
    peaksy = []
    for x in peaks_ppm:
        peaksx.append(x[0])
        peaksy.append(x[1])
    return [peaksx, peaksy]

def fn_peak_corrector (peaks, data, B0_hz):         #temp correction till i find actual cause
    xcorr_ppm = len(data)*-0.0002449
    ycorr_ppm = len(data[0])*-0.0002449
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
    fig.savefig(dir + r"\pic.png", dpi=200)
    return (fig)
