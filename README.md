# SIS (source insertion system) control code

python3, pyserial needed, Windows+Linux supported

GERDA: 3 systems, controlled from one box

LEGEND: 4 systems, controlled from two boxes (2+2)

-----

short description of scripts:


- "init.py" or "init.py <unit no.>" --> initialisation (movement to parking position, hitting the end-switch)
of either all units, or a certain unit;
expected time to finish is printed in the beginning 
(from parking position approx. 3 sec, from calibration positions approx. 10 mins);
current positions are printed in console and saved in txt file every 5 sec;
send stop commands and exit on 1 in case of errors

- "pos.py <value>" or "pos.py x <value2> <value3>" --> movement of all units to position <value>, or of certain unit(s),
in this example source 1 stays at current position (x), source 2 will be moved to <value2>, and source 3 will moved to <value3>;
for LEGEND of course with either all, or with 4 options instead of 3
(e.g. "pos.py x <value2> x x" moves only source 2 to <value2>);
expected time to finish is printed in the beginning;
current positions are printed in console and saved in txt file every 5 sec;
send stop commands and exit on 1 in case of errors;
note that units need to be initialised in order to be moved to certain positions

- "stop.py" or "stop.py <unit no.>" --> stop of a possibly ongoing movement
of either all units, or a certain unit;
current positions are printed in console and saved in txt file;
exit on 1 in case of errors
  
- "get.py" --> current positions and status bits/bytes are saved in a txt file,
most important ones are also printed in terminal

- "test_iteration.py" --> not really needed, just an example script to show how one could call the other scripts repeatedly on Windows (Python3 Anaconda interpreter), or on Linux (ubuntu kernel 4.x), plenty of other options exist as well of course)

-----


internal basic commands:

-send init command to a unit

-send target position to a unit

-send stop command to a unit

-get status of units

-get positions of units

-----

structure of calibration procedure in DAQ code (example):

-python3 init.py

-python3 pos.py 7200

-python3 pos.py 8500 x x x

-DAQ commands for data taking

-python3 pos.py 7200 8500 x x

-DAQ commands for data taking

-python3 pos.py x 7200 8500 x

-DAQ commands for data taking

-python3 pos.py x x 7200 8500

-DAQ commands for data taking

-python3 init.py (for full removal, otherwise e.g. python3 pos.py 6000 to park all sources just above the detector arrays)
