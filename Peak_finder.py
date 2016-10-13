
def peaker (dir):
    #import needed modules
    import nmrglue as ng  # NMR software


    # import user config file
    import config
    import Peak_writer as pw

    # check if in processed folder
    if "pdata" not in dir:
        return("Please use preprocessed data from topspin\nPress Enter to close...")
        exit()

    # read in the data from given dir
    dic, data = ng.bruker.read_pdata(dir)  # this has been processed with topspin; no math is needed
    dir2 = dir[:dir.find('pdata')]
    dic2 = open(dir2 + r'\acqu', 'r').read()

    # collect the parameters
    B0_hz = float(dic2[dic2.find(r'$SFO1=') + 7:dic2.find('##$SFO2')])
    SO1_hz = float(dic2[dic2.find(r'$O1=') + 5:dic2.find('##$O2')])
    SW_hz = float(dic['procs']['SW_p'])

    # peak picking
    peaks = ng.peakpick.pick(data, (data.max() * config.Default_Threshold), diag=False, cluster=True)
    print(str(peaks))

    # ppm conversion
    SW_ppm = SW_hz / B0_hz
    SO1_ppm = SO1_hz / B0_hz
    peaks_ppm = pw.fn_peak_ppm(peaks, SW_ppm, SO1_ppm, len(data), len(data[0]))
    print("parameters: b0: %f so1_hz: %f So1_ppm: %f SW_hz: %f Sw_ppm: %f" % (B0_hz, SO1_hz, SO1_ppm, SW_hz, SW_ppm))
    print(peaks_ppm)

    pw.fn_peak_xml(peaks_ppm, dir)
    if (config.Default_Plotting):
        pw.fn_data_plotter(dir, data, peaks_ppm, SW_ppm, SO1_ppm)

    return (peaks_ppm)

