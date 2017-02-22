# Towards a more general approach for the identification of sacharides.

This Master thesis aims to create a fast and easy usable way to identify sacharides using NMR spectroscopy.
This was done by altering the 1D-selTOCSY pulse program to create a 2D-selTOCSY using the mixing time as a second variable.
We have included the option to use this on multiple frequencies in one experiment; for an even easier analysis.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

For the analysis a 700MHz NMR-spectrometer was used. However the software will accept other frequencies. The only channel needed is a Hydrogen-channel.
This processing script uses Python 3.5 and was made using Anaconda. The main required modules are:

```
NMRGlue			-	http://www.nmrglue.com/
Numpy			-	http://www.numpy.org/
Scipy			-	https://www.scipy.org/
Detect Peaks	-	https://github.com/demotu/BMC - Marcos Duarte

```

### Installing (only required once)

A step by step series of examples that tell you have to get a development environment running.
It should come packaged in a **.exe** file.

```
The program has not been packaged yet. This will be done soon...
```

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

## Use the 2d-sel TOCSY Matching a.k.a. SELMA

The GUI design was made to be simple; in general it consists of two steps:

#### Get a green database status
To get a database; two steps can be taken:
* Load a database - *You can load a database from a given location; using the browse button*
```
To load; just use the browse button to go to the correct location. If the status turns blue; you have a loadable database file present; just cluck the **Load** button.
```
* Compile your own database - *You can compile your own database*
```
To compile your database; browse to a folder which contains your sacharides. The status should remain red; if a database file is present however; it will be blue.
It will prompt you to override the current database if one is present.
```
**The database will only load experiments who end on a 2 as a number; and will load the 1st processing data.**

#### Get a green experiment status
This can be done by browsing to your experiments processed folder location. Ensure the **SAMPLES.txt** file is present and you will get a blue status.
Once your status is blue; you can press the load button.

## The given output

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
* [Marcos Duarte] (https://github.com/demotu/BMC) - for his code of peak detection
* [Sean Seyler] (https://pythonhosted.org/MDAnalysis/documentation_pages/analysis/psa.html#seyler2015) - for his extended documentation on Fréchet distances

## Acknowledgments

* Thank you to prof. J. C. Martins and prof. P. Dawyndt for giving me the opportunity to work on this project.
* A big thanks to Niels Geudens for the countless questions a was allowed to ask.
* and of course all the people from the NMRSTR group.
