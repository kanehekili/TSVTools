# TSVTools  ![Screenshot](https://github.com/kanehekili/TSVTools/blob/main/src/icons/tsv_logo_100.png)

## Tools for the TSV 1847 e.V. Weilheim

All tools need python3, which can be downloaded from the python site. One python runtime is included [here](https://github.com/kanehekili/TSVTools/releases/download/V0.9/OmocC.zip). In addition pyQt6 has to be installed: (in Terminal or Windoze cmd) :

pip install pyqt6

### Omoc Comparer
![Download with python.exe V0.9](https://github.com/kanehekili/TSVTools/releases/download/V0.9/OmocC.zip)

![Download V0.9.1 update (no runtime for sane OS )](https://github.com/kanehekili/TSVTools/releases/tag/V0.9.1)

Compare booked times of a sport gym location owned by old white officals with the real occupation saved on a cloud instance (omoc). The software is only able to compare to xsls files, since it is based on openpyxl. Works with Textmaker,LibreOffice and MS.

Basic idea is to compare dates and locations in order to pay only the real time used. The input files are propriatatry. This software can therefore only used as template for similar proejcts.

The resulting file can be opened by selecting a displayed link.

#### Design Model:
The OmocComparer is the UI, using the OCModel for infos.

##### WorkSheetComparer
Reads two files (comparable to "Meld") and produces a data set of differences.

##### WorkSheetWriter
Gets the data from the comparer and writes the results into a xslx file.



Tested on Linux and Windoze(relcutantly). 

## Additional Libs:
pip install openpyxl

### More small apps will follow
