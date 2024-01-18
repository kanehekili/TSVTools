'''
Created on 18 Jan 2024

@author: matze
'''
#install python-openpyxl (arch native) or pylightxl which handles Softmaker better
from openpyxl import load_workbook
from datetime import datetime
from time import sleep
from enum import Enum
from collections import Counter
import os,sys
from itertools import tee
import gzip,time
import logging
from logging.handlers import RotatingFileHandler
import subprocess
from subprocess import Popen

class OSTools():
    #singleton, class methods only

    @classmethod
    def getLocalPath(cls,fileInstance):
        return os.path.dirname(os.path.realpath(fileInstance))
    
    @classmethod
    def fileExists(cls, path):
        return os.path.isfile(path)
    
    @classmethod
    def setMainWorkDir(cls,dirpath):
        os.chdir(dirpath)  #changes the "active directory" 
    
    @classmethod    
    def getActiveDirectory(cls):
        return os.getcwd()
    
    #@classmethod
    #def username(cls):
    #    return pwd.getpwuid(os.getuid()).pw_name 
    
    @classmethod
    def joinPathes(cls,*pathes):
        res=pathes[0]
        for _,tail in cls.__pairwise(pathes):
        #for a, b in tee(pathes):
            res = os.path.join(res, tail)
        return res
    
    def getHomeDirectory(self):
        return os.path.expanduser("~")
    
    @classmethod
    def ensureDirectory(cls, path, tail=None):
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
    
    @classmethod
    def __pairwise(cls,iterable):
        a, b = tee(iterable)
        next(b, None)
        return list(zip(a, b))    
    #logging rotation & compression
    @classmethod
    def compressor(cls,source, dest):
        with open(source,'rb') as srcFile:
            data=srcFile.read()
            bindata = bytearray(data)
            with gzip.open(dest,'wb') as gz:
                gz.write(bindata)
        os.remove(source)
    
    @classmethod
    def namer(self,name):
        return name+".gz"

    @classmethod
    def setupRotatingLogger(cls,logName,logConsole):
        '''
        Note: desktop file are opened by current user - active directory can not be used (Permissions) 
        '''
        logSize=5*1024*1024 #5MB
        if logConsole: #aka debug/development
            folder = OSTools.getActiveDirectory()    
        else:
            folder= OSTools.joinPathes(OSTools().getHomeDirectory(),".config",logName)
            OSTools.ensureDirectory(folder)
        logPath = OSTools.joinPathes(folder,logName+".log") 
        fh= RotatingFileHandler(logPath,maxBytes=logSize,backupCount=5)
        fh.rotator=OSTools.compressor
        fh.namer=OSTools.namer
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


    @classmethod
    def setLogLevel(cls,levelString):
        if levelString == "Debug":
            Log.setLevel(logging.DEBUG)
        elif levelString == "Info":
            Log.setLevel(logging.INFO)
        elif levelString == "Warning":
            Log.setLevel(logging.WARNING)
        elif levelString == "Error":
            Log.setLevel(logging.ERROR)

    #will not work in windows
    @classmethod
    def checkIfInstanceRunning(cls,moduleName):
        process = Popen(["ps aux |grep -v grep | grep "+moduleName],shell=True,stdout=subprocess.PIPE)
        result = process.communicate()
        rows = result[0].decode('utf8').splitlines()
        instanceCount =0
        for line in rows:
            if line:
                instanceCount+=1
        return instanceCount > 1


Log=logging.getLogger("OMOC")


class WorksheetReader():
    def __init__(self,filePath):
        self.file=filePath
    
    def importXls(self):
        wb = load_workbook(filename=self.file, read_only=True)
        sheets= wb.sheetnames
        ws=wb[sheets[0]]
        fullSheet=[]
        for row in ws.rows:
            singleRow=[]
            for cell in row:
                saveVal=cell.value if cell.value else '' 
                singleRow.append(saveVal)
            fullSheet.append(singleRow)
        cntMbrs=len(fullSheet)
        cntCols = len(fullSheet[0])
        Log.info("Read %d entries, with %d columns each",cntMbrs,cntCols)
        wb.close()        
        return fullSheet   

class WorksheetWriter():
    def __init__(self,filePath):
        self.file=filePath
    
    def exportXls(self,crazyArray):
        pass
    
class WorkSheetComparer():
    def __init__(self,lwArrray,omocArray):
        pass       

if __name__ == '__main__':
    pass