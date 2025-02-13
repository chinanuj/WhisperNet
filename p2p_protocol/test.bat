@echo off

start cmd /k "python seed.py 1"
start cmd /k "python seed.py 2"
start cmd /k "python seed.py 3"
start cmd /k "python seed.py 4"
start cmd /k "python seed.py 5"
start cmd /k "python seed.py 6"
start cmd /k "python seed.py 7"
start cmd /k "python seed.py 8"
start cmd /k "python seed.py 9"
start cmd /k "python seed.py 10"

start cmd /k "python peer.py 1 192.168.56.1"
start cmd /k "python peer.py 2 192.168.56.1"
start cmd /k "python peer.py 3 192.168.56.1"
start cmd /k "python peer.py 4 192.168.56.1"
start cmd /k "python peer.py 5 192.168.56.1"
start cmd /k "python peer.py 6 192.168.56.1"
start cmd /k "python peer.py 7 192.168.56.1"
start cmd /k "python peer.py 8 192.168.56.1"

timeout /t 2 /nobreak > nul
start cmd /k "type outputfile.txt && pause"
