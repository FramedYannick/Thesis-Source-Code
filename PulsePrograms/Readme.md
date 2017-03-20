## How to use the Sel-2D TOCSY
### Setup the Sel-2D TOCSY pulse program (DOWNLOAD AVAILABLE)

The experiment is based on the 1D-selTOCSY; where we vary the mixing time in every scan creating a second dimension.
For the analysis of multiple sacharides in one sample; a second loop was included to change the frequency of the selective peak and place it on the H1-region.
The code can be found in *not included yet* the pulse program file.

A DIPSI-version of the 1D-selTOCSY pulse program was used to enable zero-quantum filtering and cleaning up the spectra.
We used a modified version by D. Sinnaeve; but the standard Bruker pulse program should work.

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

The p6 duration must be set to **26.000µs and the O1 parameter must be set to 0ppm.
This will mean the half of your spectra is useless; however this is needed to ensure a correct selective pulse. Keep this in mind when choosing the TD in the f2 dimension.

In Topspin; you must change the amount of dimensions.

### Setup an experiment

This will be discussed extensively in a new file; however, a short summary:
In general; you must set P6; PLW10; SPW2 AND SPW29 for each new sample (all are dependent of the 90° pulse).
You must also set the TD; this will be thirteen times the amount of frequencies you want to measure.
In the fqlist; you must set all frequencies that you want to measure; however you must enter each frequency THIRTEEN times!

### Process an experiment

A part of the processing must still be done using the [Topspin] (https://www.bruker.com/products/mr/nmr/nmr-software/software/topspin/overview.html) from Bruker.
Using this; you must process the data in the f2 dimension; the minimum required commands are:

```
xf2; apk2d; abs2
```

However; due to the harder phasing upon using the experiment on multiple frequencies; it might be beneficial to do the phasing manually.
CAUTION; DUE TO AN ERROR WITH NMR GLUE, FOR NOW YOU MUST EXTRACT THE DATA TO A TXT FILE:
```
totxt
```
The txt file must be called ```SAMPLES.txt``` and should be stored in the processed data folder (inside pdata/1).
The program will not be working without this for now!!!

## HOw to use the 3D Band Selective TOCSY
### Setup the Sel-2D TOCSY pulse program (DOWNLOAD AVAILABLE)