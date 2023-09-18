@echo off
CLS
ECHO "Backup running. Please wait."
C:\Users\Pete\AppData\Local\Programs\Python\Python311\python.exe "C:\Users\Pete\Tools\backup.py"
ECHO Backup complete.
timeout 5 > nul
exit