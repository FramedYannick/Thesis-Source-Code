## How to use the p2D-sel TOCSY
### Setup the p2D-sel TOCSY pulse program (DOWNLOAD AVAILABLE)

The experiment is based on the 1D-selTOCSY; where we vary the mixing time in every scan creating a second dimension.
For the analysis of multiple sacharides in one sample; a second loop was included to change the frequency of the selective peak and place it on the H1-region.
The code can be found in the pulse program file.

A DIPSI-version of the 1D-sel TOCSY pulse program was used to enable zero-quantum filtering and cleaning up the spectra.
A modified version by D. Sinnaeve was used; however the standard Bruker pulse program should work.

The following changes were made in the pulse program:

```
1 ze
```
was changed into:
```
1 ze
  20u fq1:f1
  2000m
```
This is done to loop over all selected frequencies for the selective peak and add a delay when switching frequency. This will make sure the t1-relaxation is mostly gone when starting the measurement on a new frequency.
For the second and last edit; this
```
  30m mc #0 to 2 F0(zd)
```
was changed into:
```
  ;30m mc #0 to 2 F0(zd) - commented line
  d11 wr #0 if #0 ivc
  lo to 1 times td1
```
to write the data and increase the variable counter list and make td1 times the scan.

Next; we must ensure we all use the same mixing times; therefor; you must create a vclist with the content:
```
3 6 9 12 15 18 21 24 27 30 33 36 39
```
If you use a file to store the vclist; you MUST put each number on a new line!

The p6 duration must be set to **25.000µs and the O1 parameter must be set to 0ppm.
This will mean the half of your spectra is useless; however this is needed to ensure a correct selective pulse. Keep this in mind when choosing the TD in the f2 dimension.

In Topspin; you must change the amount of dimensions to two.

### Setup an experiment

In general; you must set P1; P6; PLW10; SPW2 AND SPW29 for each new sample (all are dependent of the 90° pulse):
p6 is the length of the low power pulse; used for the DIPSI sequence; to ensure compatibility with the database; set it to 25µs.
PLW10 is the power level corresponding to p6. It can be calculated using the 'calcpowlev' command in topspin.

For the selective pulse; one can test the optimal results in a 1D proton experiment; however during our setup; a 180 refocussing pulse was always used.
The length of this pulse (p12) must be set to achieve optimal selectivity (1/p12 equals to the selectivity).
The shape tool must be used to integrate the used shape; and analysis will determine the powerlevel that must be set (SPW2 = corr + PLW1).
The same can be repeated for the adiabatic pulse of 20msec (Crp60,20,20.10); although one must use 'integrate shape (adiabatic)' for integration.

One must also set the TD; this will be thirteen times the amount of frequencies you want to measure.
In the fqlist; you must set all frequencies that you want to measure; however you must enter each frequency THIRTEEN times!

### Process an experiment

A part of the processing must still be done using the [Topspin] (https://www.bruker.com/products/mr/nmr/nmr-software/software/topspin/overview.html) from Bruker.
Please set the xdim parameter to identical size as the processed software!
This is to compensate for the submatrix save format; to ensure NMRGlue can read in the processed data.
Using the standard processing commands; one must process the data in the f2 dimension; the minimum required commands are:

```
xf2 xdim; apk2d; abs2
```

However; due to the harder phasing upon using the experiment on multiple frequencies; it might be beneficial to do the phasing manually.
Identical to the phasing, optimal results will be achieved if one uses the manual base correction.

## How to use the p3D Band Selective TOCSY

The 3D-Bsel TOCSY should only be used upon high sample complexity as it has a much higher measuring time. It will yield identical results as the p2D experiment.

### Setup the p3D-Bsel TOCSY pulse program (DOWNLOAD AVAILABLE)

Due to the high complexity of changing the pulse program from a 2D to a p3D; the required steps will not be described.
It is adviced to download the pulse program from the Github page.

In general; the following edits were made:
An extra dimension was added; f2 is now the mixing dimension and f3 the indirect measurement direction.
Trimming pulses were also added to reduce the delays between scans.
At the end of the loops; the following calculations must be made:
```
F1PH(calph(ph1, -90), caldel(d0, +in0))
F2QF(calclist(vc,1))
```
Creating the indirect dimension (increment the delay) and the mixing dimension.

### Setup an experiment

Every step of the p2D experiment for the power levels and pulse durations is identical for the p3D experiment.
The dimensions of the experiment however; are different: TD = (2k/4k, 13, 64/128).
The spectral window in the f1 dimension must be as small as possible; depending of the used selective peak.
In the f3 dimension; the chemical shift of the entire spectrum must be included.

###Process an experiment

As with the p2D-sel TOCSY; one must process the data before passing it on to NMRGlue.
Please set the xdim parameter to identical size as the processed software!
This is to compensate for the submatrix save format; to ensure NMRGlue can read in the processed data.
Using the standard processing commands; one must process the data in the f3 dimension:
```
tf3 xdim; tf1; tf3p; tf1p; tabs1; tabs3
```
It can be benificial to process a single plane of the p3D experiment using xfb (in the 1-3 plane with high mixing times) to determine the optimal phase and baseline correction.
For more information; please inspect the Bruker Topspin Processing manual in the 3D-processing commands chapter.
This should be done before the tf3 command, as it will use the stored phase parameter.