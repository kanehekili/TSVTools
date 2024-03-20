'''
Created on 18 Jan 2024
QT6 implementation of Xcel sheet comparison by a retro "Landkreis" and a fairly modern web app
@author: matze
'''
import traceback, os, argparse, sys, json
from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import QtWidgets, QtGui, QtCore
import OCModel
from OCModel import Log, OSTools, WorkSheetComparer, WorkSheetWriter
from time import sleep

VERSION="0.9"
WIN=None

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
    OMOC = "OMOC"
    LKR = "LKR"
    HALLEN=("Jahnhalle","Gymnasium","FOS","Schwimmbad","Sonstige")

    def __init__(self, qapp):
        super(MainFrame, self).__init__()
        self._isStarted = False
        self.__qapp = qapp
        self.qtQueueRunning = False
        self.omocFile = None
        self.lkrFile = None
        self.configJson=None
        self.model = WorkSheetComparer()
        self.tmpSaveTarget=""
        self.setWindowIcon(getAppIcon())
        self.initUI()
        self.centerWindow()
        self.setWindowTitle("TSV Omoc Hallenputzer")
        self.show()
        # qapp.applicationStateChanged.connect(self.__queueStarted)        

    def centerWindow(self):
        frameGm = self.frameGeometry()
        centerPoint = self.screen().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    '''
    def __queueStarted(self, _state):
        if self.qtQueueRunning:
            return
        self.qtQueueRunning = True
        #self._initModel()
    '''
    '''    
    def initUI(self):
        self.init_toolbar()
        self.uiInfoLabel=QTextEdit(self)
        self.uiInfoLabel.setReadOnly(True)
        self.uiInfoLabel.setAcceptRichText(True)
        self.uiInfoLabel.setText("<h3>Omoc converter<\h3> <h4>Omoc Datei laden <img src=./icons/DownloadGreen.png width='26'> <br>Dazugehörige LKR Datei laden <img src=./icons/DownloadRed.png width='26'><\br><\h4>")
        self.uiInfoLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        box = QtWidgets.QVBoxLayout();
        box.addWidget(self.uiInfoLabel)        
        # Without central widget it won't work
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)    
        # TODO: self.resize
        wid.setLayout(box)
        self.resize(400, 450)
        
    def init_toolbar(self):
        self.omocAction = QtGui.QAction(QtGui.QIcon('./icons/DownloadGreen.png'), 'Omoc Datei', self)
        self.omocAction.setShortcut('Ctrl+O')
        self.omocAction.triggered.connect(self._onOmocFileClicked)

        self.lkrAction = QtGui.QAction(QtGui.QIcon('./icons/DownloadRed.png'), 'LKR Datei', self)
        self.lkrAction.setShortcut('Ctrl+L')
        self.lkrAction.triggered.connect(self._onLkrFileClicked)


        self.stopAction = QtGui.QAction(QtGui.QIcon('./icons/dialog-close.png'), 'Schließen', self)
        self.stopAction.setShortcut('Ctrl+H')
        self.stopAction.triggered.connect(self.goodbye)
        #self.stopAction.setEnabled(False)
        
        spacer = QtWidgets.QWidget();
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred);
        
        self.toolbar = self.addToolBar('Main')
        self.toolbar.addAction(self.omocAction)
        self.toolbar.addAction(self.lkrAction)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(spacer);
        self.toolbar.addAction(self.stopAction)   
    '''     

    def initUI(self):
        
        pix = QtGui.QPixmap("./icons/TSV-big.png")
        pix = pix.scaledToWidth(32, mode=Qt.TransformationMode.SmoothTransformation)
        self.uiLogo = QtWidgets.QLabel("")
        self.uiLogo.setPixmap(pix)
        
        self.uiTypeCombo = QtWidgets.QComboBox(self)
        self.uiTypeCombo.setEditable(False)
        #self.uiTypeCombo.currentTextChanged.connect(self._onTypeChanged)
        self.uiTypeCombo.setToolTip("Welche Halle wird verglichen?")
        self.uiTypeCombo.addItem("-Bitte Halle auswählen-")
        self.uiTypeCombo.addItems(self.HALLEN) 
        
        self.uiOmocFile= QtWidgets.QLabel(self)
        self.uiOmocFile.setText("?")
        self.uiOmocButton = QtWidgets.QPushButton(" Omoc")
        self.uiOmocButton.setIcon(QtGui.QIcon("./icons/download-folder.png"))
        self.uiOmocButton.setFixedWidth(85)
        self.uiOmocButton.setToolTip("Suche passende OMOC Datei")
        self.uiOmocButton.clicked.connect(self._onOmocFileClicked)

        self.uiLkrFile= QtWidgets.QLabel(self)
        self.uiLkrFile.setText("?")
        self.uiLkrButton = QtWidgets.QPushButton(" Lkr    ")
        self.uiLkrButton.setIcon(QtGui.QIcon("./icons/download-folder.png"))
        self.uiLkrButton.setFixedWidth(85)
        self.uiLkrButton.setToolTip("Suche passende Landkreis Datei")
        self.uiLkrButton.clicked.connect(self._onLkrFileClicked)

        self.uiInfoLabel = QTextEdit(self)
        self.uiInfoLabel.setReadOnly(True)
        self.uiInfoLabel.setAcceptRichText(True)
        self.uiInfoLabel.setHtml(self._intro())
        self.uiInfoLabel.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.uiCompareButton = QtWidgets.QPushButton("Vergleiche")
        self.uiCompareButton.setIcon(QtGui.QIcon("./icons/merge.png"))
        self.uiCompareButton.clicked.connect(self._onCompareClicked)
        self.uiCompareButton.setEnabled(False)
        
        self.uiExitButton = QtWidgets.QPushButton("Exit")
        self.uiExitButton.setIcon(QtGui.QIcon("./icons/dialog-close.png"))
        self.uiExitButton.clicked.connect(self._onExitClicked)

        self.uiTypeCombo.currentTextChanged.connect(self._onTypeChanged) #make sure button exists

        box = self._makeLayout()
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)    
        wid.setLayout(box)
        self.resize(500, 600) 
      
    def _makeLayout(self):
        mainBox = QtWidgets.QVBoxLayout()  # for all
        
        headBox = QtWidgets.QHBoxLayout()
        headBox.setSpacing(100)
        headBox.addWidget(self.uiTypeCombo,stretch=50)
        headBox.addWidget(self.uiLogo,stretch=0)
        #headBox.addWidget(self.uiLogo)
        #headBox.addStretch()
        
        btn1Box = QtWidgets.QHBoxLayout()  # btn omoc
        btn1Box.setSpacing(20)
        btn1Box.addWidget(self.uiOmocFile)
        btn1Box.addStretch()
        btn1Box.addWidget(self.uiOmocButton)
        
        btn2Box = QtWidgets.QHBoxLayout()  # btn lkr
        btn2Box.setSpacing(20)
        btn2Box.addWidget(self.uiLkrFile)
        btn2Box.addStretch()
        btn2Box.addWidget(self.uiLkrButton)
        
        btn3Box = QtWidgets.QHBoxLayout()  # btn bottom
        btn3Box.setSpacing(20)
        btn3Box.addStretch()
        btn3Box.addWidget(self.uiCompareButton)
        btn3Box.addWidget(self.uiExitButton)
        
        #mainBox.addWidget(self.uiTypeCombo)
        mainBox.addLayout(headBox)
        mainBox.addLayout(btn1Box)
        mainBox.addLayout(btn2Box)
        mainBox.addWidget(self.uiInfoLabel)
        mainBox.addLayout(btn3Box)
        
        return mainBox

    @QtCore.pyqtSlot()        
    def _onOmocFileClicked(self):
        targetPath = self.readLastXPath(self.OMOC)
        extn = "*.xlsx"
        fileFilter = "Spreadsheets (%s);;Alle Dateien(*.*)" % extn
        result = QtWidgets.QFileDialog.getOpenFileName(parent=self, directory=targetPath, caption="Lese Omoc Daten", filter=fileFilter);
        if result[0]:
            self.omocFile = result[0]
            self.uiOmocFile.setText(OSTools.fileNameOnly(self.omocFile))
            self.saveLastXPath(self.OMOC,OSTools.dirname(self.omocFile))
            self.uiInfoLabel.append("OMOC Datei gefunden")
            self._updateCompareButton()

    def _onLkrFileClicked(self):
        targetPath = self.readLastXPath(self.LKR)
        extn = "*.xlsx"
        fileFilter = "Spreadsheets (%s);;Alle Dateien(*.*)" % extn
        result = QtWidgets.QFileDialog.getOpenFileName(parent=self, directory=targetPath, caption="Lese LKR Daten", filter=fileFilter);
        if result[0]:
            self.lkrFile = result[0]
            self.uiLkrFile.setText(OSTools.fileNameOnly(self.lkrFile))
            self.saveLastXPath(self.LKR,OSTools.dirname(self.lkrFile))
            self.uiInfoLabel.append("Landkreis Datei gefunden")
            self._updateCompareButton()

    @QtCore.pyqtSlot()
    def _onExitClicked(self):
        self.close()
        
    def _onTypeChanged(self, aString):
        self.model.location = aString
        self._updateCompareButton()

    def _onCompareClicked(self):
        #we need a long running operation
        self.uiInfoLabel.append("Starte Vergleich ....")
        QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        worker = LongRunningOperation(self._startCompare)
        worker.signal.connect(self._cleanupWorker)
        worker.startOperation()
        
    def _startCompare(self):
        self.model.readOmoc(self.omocFile)
        self.model.readLkr(self.lkrFile)
        self.model.compare()
        hp = OSTools.getHomeDirectory()
        #tp = OSTools.joinPathes(path,"OMOC")
        loc = self.model.location
        self.tmpSaveTarget=OSTools.joinPathes(hp,loc+".xlsx")
        wr=WorkSheetWriter(self.tmpSaveTarget)
        wr.export(loc,("Datum","OMOC","LKR"),self.model.data)
        
        
        
    def _cleanupWorker(self, worker):
        # QThread: Destroyed while thread is still running
        msg = worker.msg 
        Log.info("Long operation done:%s",msg)
        if msg:
            self.uiInfoLabel.setHtml('<p style="color:red;"><h4>Fehler</h4>%s</p><br>Nicht nochmal probieren -> Melden macht frei!'%(msg))
        else:
            self._reportResults()
        worker.quit()
        worker.wait(); 
        QApplication.restoreOverrideCursor()   
        self._prepareNextRun() 

    def _reportResults(self):
        txt=[]
        txt.append("<h4> Vorgang beendet</h4>")
        txt.append("Buchungen gleich: %d"%(self.model.statistics[0]))
        txt.append("<br>Buchungen falsch: %d"%(self.model.statistics[1]))
        txt.append("<br>Die Ergebnisdatei wurde unter %s abgelegt"%(self.tmpSaveTarget))
        Log.info("Statistics Same:%d diff: %d",self.model.statistics[0],self.model.statistics[1])
        self.uiInfoLabel.setHtml(''.join(txt))


    def _intro(self):
        txt=[]
        txt.append("<h3>Omoc converter V%s</h3>"%(VERSION))
        txt.append(" Bitte folgende Schritte durchführen ")
        txt.append("<ul><li>Die prüfende Halle aussuchen</li>")
        txt.append("<li>Die OMOC Datei wählen <strong>[Button]</strong></li>")
        txt.append("<li>Die Landkreis(LKR) Datei wählen <strong>[Button]</strong></li>")
        txt.append("<li>Vergleiche<strong>[Button]</strong></li>")
        txt.append("</ul>")
        txt.append("<br>Viel Erfolg")
        return ''.join(txt)
        

    def _updateCompareButton(self):
        if not self.uiCompareButton:
            return
        if not self.model.location.startswith("-"): 
            if len(self.uiOmocFile.text()) > 3 and len(self.uiLkrFile.text()) > 3:
                self.uiCompareButton.setEnabled(True)
                return
        self.uiCompareButton.setEnabled(False)

    def _prepareNextRun(self):
        #self.uiInfoLabel.setHtml(self)
        self.uiTypeCombo.setCurrentIndex(0)
        self.uiLkrFile.setText("?")
        self.uiOmocFile.setText("?")
        self.tmpSaveTarget=""
        #self.uiCompareButton.setEnabled(False)
        

    def readLastXPath(self, part):
        if not self.configJson:
            self.configJson={}
            cfg = self._configPath()
            if OSTools.fileExists(cfg):
                with open(cfg) as jsonFile:
                    self.configJson = json.load(jsonFile)
            
        return self.configJson.get(part,None)

    def saveLastXPath(self,part,path):
        self.configJson[part]=path
        cfg = self._configPath()
        with open(cfg, 'w') as jsonFile:
            json.dump(self.configJson, jsonFile)

    def _configPath(self):
        folder = OSTools.joinPathes(OSTools().getHomeDirectory(), ".config")
        OSTools.ensureDirectory(folder)
        return OSTools.joinPathes(folder, "omoc.json") 

    
''' Long running operations for actions that do not draw or paint '''        
class LongRunningOperation(QtCore.QThread):
    signal = pyqtSignal(object) 

    def __init__(self, func, *args):
        QtCore.QThread.__init__(self)
        self.function = func
        self.arguments = args
        self.msg=None

    def run(self):
        try:
            self.function(*self.arguments)
        except Exception as ex:
            Log.exception("***Error in LongRunningOperation***")
            self.msg = "Daten konnten nicht gelesen werden"
        finally:
            self.signal.emit(self)

    def startOperation(self):
        self.start()  # invokes run - process pending QT events
        sleep(0.5)
        QtCore.QCoreApplication.processEvents() 
        print("Events processed")   


def getAppIcon():
    return QtGui.QIcon('./icons/TSV-control.png')


def handle_exception(exc_type, exc_value, exc_traceback):
    """ handle all exceptions """
    if WIN is not None:
        infoText = str(exc_value)
        detailText = "*".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        #WIN.getErrorDialog("Unexpected error", infoText, detailText).show()
        Log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def parse():
    parser = argparse.ArgumentParser(description="OmocComparer")
    parser.add_argument('-d', dest="debug", action='store_true', help="Debug logs")
    #parser.add_argument('-f', dest="headless", type=str, default=None, help="execute without GUI with filename", metavar="FILE")
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
        # fn = args.headless
        # if fn is not None:
        #    headlessImport(fn)
        #    return 0
        Log.info("--- Start Omoc comparer ---")
        argv = sys.argv
        app = QApplication(argv)
        app.setWindowIcon(getAppIcon())
        WIN = MainFrame(app)  # keep python reference!
        # ONLY windoze, if ever: app.setStyleSheet(winStyle())
        # app.setStyle(QtWidgets.QStyleFactory.create("Fusion"));
        app.exec()
        
    except:
        with open('/tmp/error.log', 'a') as f:
            f.write(traceback.format_exc())
        traceback.print_exc(file=sys.stdout)
        Log.exception("Error in main:")
        # ex_type, ex_value, ex_traceback
        sys_tuple = sys.exc_info()
        QtWidgets.QMessageBox.critical(None, "Error!", str(sys_tuple[1]))


if __name__ == '__main__':
    sys.excepthook = handle_exception
    sys.exit(main(parse()))
    
