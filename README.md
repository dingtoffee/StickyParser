# StickyParser 
### A Windows Sticky Notes Parser (snt and plum.sqlite supported)  - Recovery of sqlite/plum sqlite also supported.


For latest version of StickyNote, 
* Copy  everything under the ```%LOCALAPPDATA%\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState```. 
* Run StickyPraser against the copied folder. Make sure the other files apart from the plum.sqlite are all in the same folder. Once run, WAL/SHMfiles will be merged into .sqlite file.
* Execute StickyPasrser
* Result csv will be created under the directory you specified. 
* All timestamps are recorded in UTC.

For legacy snt format of StickyNote, 
* Copy StickyNotes.snt under ``` C:\Users\User\AppData\Roaming\StickyNotes\```
* Run StickyPraser against the StickyNotes.snt
* Result csv will be created under the directory you specified. 
* All timestamps are recorded in UTC.

Additional Features: 
* Support recovery of deleted content of plum.sqlite. 
* Result will be created under the directory you specified. 

Support Python Version 3.x only. 
# Usage 
```
usage: stickyparser.py [-h] [-s [snt file]] [-p [sqlite file]] [-d [File Directory]] [-r [sqlite file]]

StickyParser: Parses sticky note files in legacy snt formats or latest sqlite formats.It can also be used to recover
deleted content inside sqlite. For latest version of StickyNote, please copy everything under the
%LOCALAPPDATA%\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbw\LocalStatealState Folder. Run StickyPraser against
the copied folder. Make sure the other files apart from the plum.sqlite are all in the same folder. Once run, WAL/SHM
files will be merged into .sqlite file.

optional arguments:
  -h, --help           show this help message and exit
  -s [snt file]        Sticky note .snt file. Example: StickyParser.exe -s C:\Users\User\AppData\Roaming\Sticky
                       Notes\StickyNotes.snt. Choose either -s or -p only.
  -p [sqlite file]     Sticky note plum.sqlite file. Example: StickyParse -s <Path>\plum.sqlite. Choose either -s or
                       -p
  -d [File Directory]  Specify the directory where the output should write to. Example: StickyParser -p <path> -d
                       C:\Users\User\Desktop\
  -r [sqlite file]     To recover deleted content from sqlite.
 ```
 
# Example Commands 
* Parse snt file 
```
python stickyparser.py -s "C:\Users\User\AppData\Roaming\StickyNotes\StickyNotes.snt" -d C:\temp 
```
* Parse plum.sqlite file 
```
python stickyparser.py -p %LOCALAPPDATA%\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite -d C:\temp
```
* Recovery of deleted content inside plum.sqlite (it may also support generic sqlite3 file) 
```
python stickyparser.py -r %LOCALAPPDATA%\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite -d C:\temp
```
# Example Outputs 
SNT Paser Output 
![SNT Praser Output](https://github.com/dingtoffee/StickyParser/blob/master/legacy_snt_output.JPG)
Plum Sqlite Paser Output 
![Plum Sqlite Paser Output](https://github.com/dingtoffee/StickyParser/blob/master/plum_output.JPG)

# References 
https://github.com/aramosf/recoversqlite
https://gist.github.com/daddycocoaman/e1a4f31109e17188d5ce8fd0ca15b63e
