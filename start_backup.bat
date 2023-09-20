REM This batch file is to be used as a program to be run at log-in by
REM the Windows Task Scheduler. By starting backup.bat via a shortcut 
REM whose properties are set to make it run minimised, the user will
REM experience the minimum disturbance possible. The shortcut itself
REM is not a text file and needs to be made by hand on the user's PC.
start "" "D:\Users\Pete\Tools\Windows\backup.bat - Shortcut.lnk"
exit