# Towards a more general approach for the identification of sacharides.

This Master thesis aims to create a fast and easy usable way to identify sacharides using NMR spectroscopy.
This was done by altering the 1D-selTOCSY pulse program to create a 2D-selTOCSY using the mixing time as a second variable.
We have included the option to use this on multiple frequencies in one experiment; for an even easier analysis.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

For the analysis a 700MHz NMR-spectrometer was used. The only channel needed is a Hydrogen-channel.
This processing script uses Python 3.5; it was made using Anaconda. The main required modules are:

```
NMRGlue			-	http://www.nmrglue.com/
Numpy			-	http://www.numpy.org/
Scipy			-	https://www.scipy.org/
Detect Peaks	-	https://github.com/demotu/BMC - Marcos Duarte

```

### Installing 

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Usage and setup for analysis

### Setup the pulse program (only required once)

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

### Setup an experiment

This will be discussed extensively in a new file; however, a short sumary:
In general; you must set P6; PLW10; SPW2 AND SPW29 for each new sample (all are dependent of the 90° pulse).
You must also set the TD; this will be thirteen times the amount of frequencies you want to measure.
In the fqlist; you must set all frequencies that you want to measure; however you must enter each frequency THIRTEEN times!


### Setup the processing tools

```
Give an example
```

## Examples

Explain what these tests test and why

```
Give an example
```

## Authors

* **Yannick Dandois** 	- *Master student* 	- [UGent github](https://github.ugent.be/ydandois) / [Github.com](https://github.com/FramedYannick)
* **J.C. Martins** 		- *Promotor* 		- [UGent biblio](https://biblio.ugent.be/person/801000687646)
* **P. Dawyndt** 		- *Copromotor* 		- [UGent biblio](http://www.twist.ugent.be/index.php?page=personeel&ugentid=801001355633)

See also the list of [contributors](https://github.ugent.be/ydandois/Thesis-Source-Code/graphs/contributors) who participated in this project.

## Give credit where it is due.

Some code was used from these people or pages their suggestion:
* [Flutefreak7] (http://stackoverflow.com/users/1639671/flutefreak7) - for his code of R-square
* 

## Acknowledgments

* Thank you to prof. J. C. Martins and prof. P. Dawyndt for giving me the opportunity to work on this project.
* A big thanks to Niels Geudens for the countless questions a was allowed to ask.
* and of course all the people from the NMRSTR group.
