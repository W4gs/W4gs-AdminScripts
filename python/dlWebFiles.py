#Requirements: pip install validators

import os
import sys
import time
import shutil
import string
import random
import hashlib
import requests
import validators

from bs4 import *
from urllib.parse import urlparse

strDownloadLoc = os.getcwd()
strDownloadFinFile = "success.txt"

intLowerSleep = 5
intUpperSleep = 20

#--------------------------------------------------------------------------------------------------
# Configuration Section
# arrURL: Enter your specific web addresses in an array format.
# arrScanExts: The extensions of the specific files you want downloaded
arrURL = [ "" ]
arrScanExts = [ "zip", "tar", "gz", "doc", "docx", "xls", "xlsx", "csv", "pdf", "ppt", "txt" ]
# End Configuration Section
#--------------------------------------------------------------------------------------------------

arrRetURLS = []
arrDeDupCheck = []
arrDLFin = []
srrURLScan = [ ]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def PrintError(strMessage):
    print("[" + bcolors.FAIL + "!" + bcolors.ENDC + "] " + strMessage)
    
def PrintSuccess(strMessage):
    print("[" + bcolors.OKGREEN + "✓" + bcolors.ENDC + "] " + strMessage)
    
def PrintStatus(strMessage):
    print("[" + bcolors.WARNING + "?" + bcolors.ENDC + "] " + strMessage)
    
def PrintSleep(strMessage):
    print("[" + bcolors.OKCYAN + "-" + bcolors.ENDC + "] " + strMessage)

def GenerateRandom():
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=random.randint(intLowerSleep, intUpperSleep)))

def SleepRandom():
    sleepRand = random.randrange(intLowerSleep, intUpperSleep)
    PrintSleep("Sleeping " + str(sleepRand))
    time.sleep(sleepRand)

def dlSuccess(strURL):
    try:
        frOpen = open(strDownloadFinFile, "a")
        frOpen.write(strURL + "\n")
        frOpen.close()
    except Exception as e:
        PrintError("Error Appending URL to Downloads File: " + strURL + str(e))

def dlReload():
    try:
        arrDLFin.clear()
        frOpen = open(strDownloadFinFile, "r")
        for tLine in frOpen:
            arrDLFin.append(tLine)
        frOpen.close()
        PrintSuccess("Loaded [" + str(len(arrDLFin)) + "] cached downloads")
        PrintSuccess("Downloads Total Spidered: [" + str(len(arrURL)) + "]")
    except Exception as e:
        PrintError("Error Opening Downloads File! " + str(e))

def DownloadThisFile(strURL, strDestination):
    try:
        r = requests.get(strURL, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(strDestination, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            PrintSuccess("Finished Downloading " + strURL)
            dlSuccess(strURL)
            dlReload()
        else:
            PrintError("Error Downloading " + strURL)
    except Exception as e:
        PrintError("Error Downloading " + strURL + " " + str(e))
    SleepRandom()

def procImages(arrImages, strDomain):
    try:
        strDownloadLoc = None
        for i, image in enumerate(arrImages):
            if (image["href"].find(strDomain) < 0):
                strURLParsed = strDomain + image["href"]
            else:
                strURLParsed = image["href"]
            for strTExt in arrScanExts:
                if (strURLParsed.find("." + strTExt) > 0):
                    if ((strURLParsed + "\n") not in arrDLFin):
                        if (strDownloadLoc is None):
                            strDownloadLoc = os.path.join(os.getcwd(), urlparse(strURL).netloc, GenerateRandom())
                        if not os.path.exists(strDownloadLoc):
                            os.makedirs(strDownloadLoc, exist_ok=True)
                        tfName = urlparse(strURLParsed)
                        PrintStatus("Downloading " + strURLParsed + " to " + os.path.join(strDownloadLoc) + "/" + str(os.path.basename(tfName.path)))
                        DownloadThisFile(strURLParsed, os.path.join(strDownloadLoc) + "/" + str(os.path.basename(tfName.path)))
                else:
                    if not ((strURLParsed) in arrURL):
                        arrURL.append(strDomain + image["href"])
        strDownloadLoc = None
    except Exception as e:
        strDownloadLoc = None
        pass

dlReload()
for strURL in arrURL:
    try:
        if (validators.url(strURL)):
            if not (strURL in srrURLScan):
                if not (os.path.exists(os.path.join(os.getcwd(), urlparse(strURL).netloc))):
                    os.mkdir(os.path.join(os.getcwd(), urlparse(strURL).netloc))
                PrintStatus("Web Request Processing " + strURL)
                srrURLScan.append(strURL)
                r = requests.get(strURL)
                soup = BeautifulSoup(r.text, 'html.parser')
                images = soup.findAll('a')
                if (strURL.find("https") != -1):
                    procImages(images, "https://" + urlparse(strURL).netloc)
                else:
                    procImages(images, "http://" + urlparse(strURL).netloc)
        else:
            PrintError("Error on URL " + strURL)
    except:
        PrintError("Error on URL " + strURL)
