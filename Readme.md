# Towards a more general approach for the identification of saccharides.

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
```
If you are using the packaged version; no python modules are needed at all.

### Installing

There are two different pulse programs available; one as an array of 1D-sel TOCSY's using the DIPSI spin lock sequence; called the sel-2D TOCSY. This is used for non complex mixtures where the anomeric peaks are well seperated. The measurement time is dependant on the amount of monosaccharides; and the setting up is more extended.
However, in general this is the fastest measurement method in case of limited measurement time.
The second pulse program; a band selective 3D-TOCSY, has longer measurement time; but is much better to seperate the anomeric signals.
Both pulse programs can be found [here](https://github.ugent.be/ydandois/Thesis-Source-Code/tree/master/PulsePrograms).

For the processing software, you also have two options; you can download the prepackaged file from the github (just under 200MB) or you can download the raw code (not recommended).
It should come packaged in a **.exe** file.

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

### Running the Database comparison
If both your experiment and database status labels are green; you can run the database search.
If you only want the search to be executed on specific chunks; please set it under the quick settings. A message box will appear to ask which chunks it should integrate.
The numbers should be seperated by commas; and may not be higher then the highest chunk. An example is given below:
```
1,2,5
```
If you want specific plots while the database search is executed; make sure to set them on the bottom left corner.
Please remember that the GUI might be *Non responding* during the search; this is completely normal.

## The given output

For a sucrose sample; using the Fréchet-method; the given output will be:

```
            Results:
-----------------------------------
    0: 0.615 a-Glucopyr.
    0: 0.223 a-Xylopyr.
    0: 0.215 b-Arabinopyr.
-----------------------------------
```

The closer the value is to 1.0; the better the match. 1.0 means an identical match of the sacharide. Please keep in mind that this is a calculated value; and errors might occur during integration.
Always use the Chunk plot to double check the curves; to ensure the correctness of your results.

## Authors

* **Yannick Dandois** 	- *Master student* 	- [UGent github](https://github.ugent.be/ydandois) / [Github.com](https://github.com/FramedYannick)
* **J.C. Martins** 		- *Promotor* 		- [UGent biblio](https://biblio.ugent.be/person/801000687646)
* **P. Dawyndt** 		- *Copromotor* 		- [UGent biblio](http://www.twist.ugent.be/index.php?page=personeel&ugentid=801001355633)

See also the list of [contributors](https://github.ugent.be/ydandois/Thesis-Source-Code/graphs/contributors) who participated in this project.

## Give credit where it is due!

Some code was used from these people or pages their suggestion:
* [Flutefreak7] (http://stackoverflow.com/users/1639671/flutefreak7) - for his code of R-square
* [Marcos Duarte] (https://github.com/demotu/BMC) - for his code of peak detection
* [Sean Seyler] (https://pythonhosted.org/MDAnalysis/documentation_pages/analysis/psa.html#seyler2015) - for his extended documentation on Fréchet distance

## Acknowledgments

* Thank you to prof. J. C. Martins and prof. P. Dawyndt for giving me the opportunity to work on this project.
* A big thanks to Niels Geudens for the countless questions a was allowed to ask.
* and of course all the people from the NMRSTR group.
