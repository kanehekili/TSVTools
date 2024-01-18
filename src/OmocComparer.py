'''
Created on 18 Jan 2024
QT6 implementation of Xcel sheet comparison by a retro "Landkreis" and a fairly modern web app
@author: matze
'''
import traceback,os,argparse,sys,json
from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtCore import Qt,pyqtSignal
from PyQt6 import QtWidgets, QtGui, QtCore
import OCModel
from OCModel import Log,OSTools

'''
Unbelievable windows crap: To get your icon into the task bar:
'''
if os.name == 'nt':
    import ctypes
    myappid = 'tsv.omoc.compare'  # arbitrary string
    cwdll = ctypes.windll  # @UndefinedVariable
    cwdll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# #Main App Window. 
class MainFrame(QtWidgets.QMainWindow):
    
    def __init__(self, qapp):
        super(MainFrame, self).__init__()
        self._isStarted = False
        self.__qapp = qapp
        self.qtQueueRunning = False
        self.sourceFile=None
        self.model
        self.setWindowIcon(getAppIcon())
        self.initUI()
        self.centerWindow()
        self.setWindowTitle("TSV Omoc Whatever")
        self.show()
        qapp.applicationStateChanged.connect(self.__queueStarted)        

    def centerWindow(self):
        frameGm = self.frameGeometry()
        centerPoint = self.screen().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def __queueStarted(self, _state):
        if self.qtQueueRunning:
            return
        self.qtQueueRunning = True
        self._initModel()
        
    def initUI(self):
        pass

def getAppIcon():
    return QtGui.QIcon('./icons/TSV-import.png')


def handle_exception(exc_type, exc_value, exc_traceback):
    """ handle all exceptions """
    if WIN is not None:
        infoText = str(exc_value)
        detailText = "*".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        WIN.getErrorDialog("Unexpected error", infoText, detailText).show()
        Log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def parse():
    parser = argparse.ArgumentParser(description="OmocComparer")
    parser.add_argument('-d', dest="debug", action='store_true', help="Debug logs")
    parser.add_argument('-f', dest="headless", type=str, default=None, help="execute without GUI with filename",metavar="FILE")
    return parser.parse_args() 

def main(args):
    try:
        global Log
        global WIN
        wd = OSTools.getLocalPath(__file__)
        OSTools.setMainWorkDir(wd)
        OSTools.setupRotatingLogger("Omoc", args.debug)
        Log = OCModel.Log
        if args.debug:
            OSTools.setLogLevel("Debug")
        else:
            OSTools.setLogLevel("Info")
        #fn = args.headless
        #if fn is not None:
        #    headlessImport(fn)
        #    return 0
        Log.info("--- Start Omoc comparer ---")
    except:
        with open('/tmp/error.log','a') as f:
            f.write(traceback.format_exc())
        traceback.print_exc(file=sys.stdout)
        Log.exception("Error in main:")
        # ex_type, ex_value, ex_traceback
        sys_tuple = sys.exc_info()
        QtWidgets.QMessageBox.critical(None, "Error!", str(sys_tuple[1]))
if __name__ == '__main__':
    pass