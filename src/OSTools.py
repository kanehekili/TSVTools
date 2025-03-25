'''
Created on Feb 3, 2025

@author: matze
'''

import os, sys
import logging
from logging.handlers import RotatingFileHandler
from itertools import tee
#import configparser
import gzip
import subprocess
from subprocess import Popen

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def getPathWithoutExtension( aPath):
    if aPath:
        # rawPath = os.path.splitext(str(aPath))[0]
        rawPath = os.path.splitext(aPath)[0]
    else:
        rawPath = ""
    return rawPath

def getExtension(path,withDot=True):
    comp = os.path.splitext(path)
    if len(comp)>1: 
        if withDot:
            return comp[1]
        else:
            return comp[1][1:]
    return comp[0]

def getDirectory(aPath):
    return os.path.dirname(aPath)

#that is the directory where this file resides - not the main
#should be used carefully (OK if FFMPEGTools in the same path as main)
def getWorkingDirectory():
    #os.path.dirname(os.path.realpath(__file__)) > if symlinks a necessary
    return os.path.dirname(os.path.abspath(__file__))               

def setMainWorkDir(dirpath):
    os.chdir(dirpath)  #changes the "active directory"  
     
#location of "cwd", i.e where is bash..
def getActiveDirectory():
    return os.getcwd()

'''
__file__ is the pathname of the file from which the module was loaded
This is the only way to ensure the correct working dir, as this module may be 
located not in the same path as the main module.
Therefore fileInstance is expected to be __file__ (but not compulsary)
! Fix: If called by link, abspath(__file__) is the cwd of the link ... 
'''
def getLocalPath(fileInstance):
    return os.path.dirname(os.path.realpath(fileInstance))

#check if filename only or the complete path
def isAbsolute(path):
    return os.path.isabs(path)

#The users home directory - not where the code lies
def getHomeDirectory():
    return os.path.expanduser("~")

def getFileNameOnly( path):
    return os.path.basename(path)

def fileExists( path):
    return os.path.isfile(path)

def removeFile( path):
    if fileExists(path):
        os.remove(path)

def canWriteToFolder(path):
    return os.access(path,os.W_OK)

def canReadFromFolder(path):
    return os.access(path,os.R_OK)

def ensureDirectory( path, tail=None):
    # make sure the target dir is present
    if tail is not None:
        path = os.path.join(path, tail)
    if not os.access(path, os.F_OK):
        try:
            os.makedirs(path)
            os.chmod(path, 0o777) 
        except OSError as osError:
            logging.log(logging.ERROR, "target not created:" + path)
            logging.log(logging.ERROR, "Error: " + str(osError.strerror))

def ensureFile( path, tail):
    fn = os.path.join(path, tail)
    ensureDirectory(path, None)
    with open(fn, 'a'):
        os.utime(fn, None)
    return fn

def joinPathes(*pathes):
    res=pathes[0]
    for head,tail in __pairwise(pathes):
    #for a, b in tee(pathes):
        res = os.path.join(res, tail)
    return res

def __pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return list(zip(a, b))

def isRoot():
    return os.geteuid()==0

def countFiles(aPath,searchString):
    log_dir=os.path.dirname(aPath)
    cnt=0
    for f in os.listdir(log_dir):
        if searchString is None or searchString in f:
            cnt+=1
    return cnt


#will not work in windows
def checkIfInstanceRunning(moduleName):
    process = Popen(["ps aux |grep -v grep | grep "+moduleName],shell=True,stdout=subprocess.PIPE)
    result = process.communicate()
    rows = result[0].decode('utf8').splitlines()
    instanceCount =0
    for line in rows:
        if line:
            instanceCount+=1
    return instanceCount > 1

#logging rotation & compression
def compressor(source, dest):
    with open(source,'rb') as srcFile:
        data=srcFile.read()
        bindata = bytearray(data)
        with gzip.open(dest,'wb') as gz:
            gz.write(bindata)
    os.remove(source)

def namer(name):
    return name+".gz"


def setupRotatingLogger(logName,logConsole):
    logSize=5*1024*1024 #5MB
    if logConsole: #aka debug/development
        folder = getActiveDirectory()    
    else:
        folder= joinPathes(getHomeDirectory(),".config",logName)
        ensureDirectory(folder)
    logPath = joinPathes(folder,logName+".log") 
    fh= RotatingFileHandler(logPath,maxBytes=logSize,backupCount=5)
    fh.rotator=compressor
    fh.namer=namer
    logHandlers=[]
    logHandlers.append(fh)
    if logConsole:
        logHandlers.append(logging.StreamHandler(sys.stdout))    
    logging.basicConfig(
        handlers=logHandlers,
        #level=logging.INFO
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s : %(message)s'
    )
    #console - only if needed
    '''
    if logConsole:
        cons = logging.StreamHandler(sys.stdout)
        logger.addHandler(cons)    
    '''
def setLogLevel(levelString):
    if levelString == "Debug":
        Log.setLevel(logging.DEBUG)
    elif levelString == "Info":
        Log.setLevel(logging.INFO)
    elif levelString == "Warning":
        Log.setLevel(logging.WARNING)
    elif levelString == "Error":
        Log.setLevel(logging.ERROR)
        
Log=logging.getLogger("Main")
        