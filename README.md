# TSVTools  ![Screenshot](https://github.com/kanehekili/TSVTools/blob/main/src/icons/tsv_logo_100.png)

## Tools for the TSV 1847 e.V. Weilheim

All tools need python3, which can be downloaded from the python site. 

The first zip file of each tool will have a python.exe included for Windows users. Later versions include the code, but no python runtime 

In addition pyQt6 has to be installed: (in Terminal or Windoze cmd) :

pip install pyqt6

### Omoc Comparer
![Download with python.exe V0.9](https://github.com/kanehekili/TSVTools/releases/tag/V0.9)

![Download V0.9.1 update (code only)](https://github.com/kanehekili/TSVTools/releases/tag/V0.9.1)

![Screenshot](https://github.com/kanehekili/TSVTools/blob/main/OmocX1.png)

Compare booked times of a sport gym location owned by old white officals with the real occupation saved on a cloud instance (omoc). The software is only able to compare to xsls files, since it is based on openpyxl. Works with Textmaker,LibreOffice and MS.

Basic idea is to compare dates and locations in order to pay only the real time used. The input files are propriatatry. This software can therefore only used as template for similar proejcts.

The resulting file can be opened by selecting a displayed link.
![Screenshot](https://github.com/kanehekili/TSVTools/blob/main/OmocX2.png)

There are not intentions to support any language support. - The stuff is german - hardcoded

#### Design Model:
The OmocComparer is the UI, using the OCModel for infos.

##### WorkSheetComparer
Reads two files (comparable to "Meld") and produces a data set of differences.

##### WorkSheetWriter
Gets the data from the comparer and writes the results into a xslx file.

#### Additional Libs:
pip install openpyxl

Runs on Linux and Windoze (no installer)

###Impresser - Front End for Impressive Slide Show
![Screenshot](https://github.com/kanehekili/TSVTools/blob/main/Impressor.png)
Impresser will copy your local files to a remote device which runs Martin Fiedlers "Impressive" Software. We are using rsync via ssh to sync the data with the remove device.

The remote device needs to have a ssh key in order to connect. 

Impressive runs on a Raspi Zero2W with RaspianOS bookworm. The target needs to have a "slides" folder in the home directory. Thumbnails are synced, pictures are currently added, but not removed (WIP) 

####Prerequisites Impressive
* apt install python3-pygame python3-pil mupdf-tools libegl-dev
* apt install impressive --no-install-recommends

####Prerequisites Impresser
* python-pyqt6 or equivalent
* rsync 

####Caveats Impressive (the slide show)
* The clock switch does not work with the framebuffer 
* Does not run on Bullseye, but on Bookworm. 
* X11 has to be installed - but is not running. 
* This code has NOT been tested with Windows
* Current Version has deprecation errors.


### More small apps will follow
