'''
Created on Mar 25, 2025
Clent front end to configure the remote - embedded - impression service on raspi
Adjust remote paths.
This app supports the configuration of "impressive" by Martin Fiedler from a remote client. 
Data will be synced by rsync, thumbs are created by magic.
This code is not intended to run on windows
@author: kanehekili
'''

'''
Icons by 
Tactice - Cristal Intensce Icons Pack under the 
CC Attribution-Noncommercial-No Derivate 4.0 Licence 
Ampeross - Qetto 2 Icons Theme
'''

import sys,time
import shutil
import subprocess,traceback, argparse
from PyQt6.QtWidgets import (
    QApplication, QWidget, QListWidget, QVBoxLayout, QPushButton, 
    QHBoxLayout, QListWidgetItem, QFileDialog, QFrame, QLabel
)
from PyQt6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent
#from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtCore import  pyqtSignal,Qt,QThread,QCoreApplication
from PyQt6 import QtWidgets,QtGui
import OSTools 

base = OSTools.getLocalPath(__file__) # we might use .local/share?
SLIDES_DIR = "slides"
SLIDER_FILE= "slidelist.txt"
THUMBS_DIR ="thumbs"
REMOTE_SLIDER_FOLDER="/home/jim/slides"

LOCAL_SLIDE_DIR = OSTools.joinPathes(base,SLIDES_DIR)
LOCAL_THUMBS_DIR = OSTools.joinPathes(base,SLIDES_DIR, THUMBS_DIR)
LOCAL_SLIDER_LIST_FILE = OSTools.joinPathes(base,SLIDES_DIR, SLIDER_FILE) #might be in the .config region
REMOTE_SLIDER_FILE = OSTools.joinPathes(REMOTE_SLIDER_FOLDER,SLIDER_FILE)
REMOTE_THUMBS_FOLDER=OSTools.joinPathes(REMOTE_SLIDER_FOLDER,THUMBS_DIR)


OSTools.ensureDirectory(LOCAL_THUMBS_DIR) #Path promblem on deploy


def create_thumbnail(file_path, thumb_path):
    try:
        subprocess.run(["magick", file_path, "-thumbnail", "250", thumb_path], check=True)
    except subprocess.CalledProcessError:
        print(f"Failed to create thumbnail for {file_path}")

def sync_files(src_dir, target_dir):
    rsync_command = [
        "rsync", "-avz", "--update", "--progress",src_dir,target_dir
    ]
    Log.info("Sync data: %s",rsync_command)
    try:
        subprocess.run(rsync_command, check=True)
        print("Sync completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during sync: {e}")

# Example usage
#local_directory = "/path/to/local/directory/"
#remote_host = "remote_alias"  # Defined in ~/.ssh/config
#remote_directory = "/path/to/remote/directory/"

#sync_files(local_directory, remote_host, remote_directory)


class ThumbnailListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setIconSize(QPixmap(100, 100).size()) 
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setDragDropOverwriteMode(False)   
        self.setAlternatingRowColors(True)
    
    def loadFileList(self):
        if not OSTools.fileExists(LOCAL_SLIDER_LIST_FILE):
            return
        with open(LOCAL_SLIDER_LIST_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.addItemToList(line)
    
    def addItemToList(self, file_path):
        filename = OSTools.getFileNameOnly(file_path)
        if filename != file_path: #no thumbnail
            #check if file exists...
            dest_path = OSTools.joinPathes(LOCAL_SLIDE_DIR, filename)
            if not OSTools.fileExists(dest_path):
                shutil.copy(file_path, dest_path)
        
        item = QListWidgetItem()
        #truncName = os.path.splitext(filename)[0]
        truncName= OSTools.getPathWithoutExtension(filename)
        #displayName = truncName+"."+os.path.splitext(filename)[1]
        displayName = truncName+OSTools.getExtension(filename)
        thumb_path = OSTools.joinPathes(LOCAL_THUMBS_DIR, truncName + ".png")
        
        if not OSTools.fileExists(thumb_path):
            create_thumbnail(dest_path, thumb_path)
        
        icon = QIcon(QPixmap(thumb_path)) if OSTools.fileExists(thumb_path) else QIcon() #need a question mark icon
        item.setText(displayName)
        item.setIcon(icon)
        self.addItem(item)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(valid_extensions):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                #valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf")
                #if os.path.isfile(file_path) and file_path.lower().endswith(valid_extensions):
                self.addItemToList(file_path)
                #save file to dedicated folder?
                #save thumbnail to dedicated forlder?
            self.repaint()
            event.acceptProposedAction()
        else:
            event.ignore()

class MainApp(QWidget):
    def __init__(self,qapp,device):
        super().__init__()
        self.beamer=device
        self.qtQueueRunning = False
        self.setWindowTitle("Info Screen") #we might configure this!
        self.setGeometry(100, 100, 600, 500)
        self._initUI()
        #TODO expand this to drop down list, with "device" as default
        self.label.setText("Gerät: "+device)
        self.show()
        qapp.applicationStateChanged.connect(self.__queueStarted)  

    
    def __queueStarted(self):
        if self.qtQueueRunning:
            return
        self.qtQueueRunning = True
        
        worker = LongRunningOperation(self.loadData)
        self.statusbar.showMessage("Die Daten werden vom Gerät gelesen...")
        worker.signal.connect(self._loadDone)
        # start the worker thread. 
        worker.startOperation()
 
    def _loadDone(self, worker):
        msg = worker.msg
        if not msg: 
            self.statusbar.showMessage("Bereit")
        else:
            self.statusbar.showMessage("Fehler:"+msg)
            Log.warning("Error while loading:%s",msg)
        self.listWidget.loadFileList() 
        
            
    def loadData(self):
        Log.info("loading data from remote device:%s",self.beamer)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        #connect to device. scp thumbs & sliderlister
        #time.sleep(5)
        #1)rsync -avz --update --progress beamer1:/home/jim/slides/slidelist.txt /home/matze/git/TSVTools/src/InfoScreen/list/
        #2) rsync -avz --update --progress beamer1:/home/jim/slides/thumbs /home/matze/git/TSVTools/src/InfoScreen/list/

        sync_files(f"{self.beamer}:{REMOTE_SLIDER_FILE}",LOCAL_SLIDE_DIR+"/")
        sync_files(f"{self.beamer}:{REMOTE_THUMBS_FOLDER}",LOCAL_SLIDE_DIR+"/")
        QApplication.restoreOverrideCursor()
    
    def saveData(self):
        Log.info("saving data to remote device:%s",self.beamer)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        with open(LOCAL_SLIDER_LIST_FILE, "w") as f:
            for index in range(self.listWidget.count()):
                f.write(self.listWidget.item(index).text() + "\n")        
        #connect to device. rsync thumbs & sliderlister
        #rsync -avzn --update --progress /home/matze/git/TSVTools/src/InfoScreen/list/ beamer1:/home/jim/slides/
        self.cleanUpFiles()
        srcFolder = OSTools.joinPathes(base,SLIDES_DIR+"/")
        sync_files(srcFolder,f"{self.beamer}:{REMOTE_SLIDER_FOLDER}/")
        
        
        QApplication.restoreOverrideCursor()
    
    def cleanUpFiles(self):
        #remove all slides and thumbs, that are NOT in the slider list
        validFiles=[]
        with open(LOCAL_SLIDER_LIST_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    fileOnly = OSTools.getPathWithoutExtension(line)
                    print(line,"[",fileOnly,"]")
                    validFiles.append(fileOnly)
        for fn in validFiles:
            pass            
                    
        
    def _saveDone(self,worker):
        msg = worker.msg
        if not msg: 
            self.statusbar.showMessage("Bye")
            self.close()
        else:
            self.statusbar.showMessage("Fehler:"+msg)
            Log.warning("Error while saving:%s",msg)            
        
    def _initUI(self):
        mainLayout = QVBoxLayout()
        
        self.label = QLabel("")
        mainLayout.addWidget(self.label)
        
        listButtonLayout = QHBoxLayout()
        listLayout = QVBoxLayout()
        buttonLayout = QVBoxLayout()        
        
        
        self.listWidget = ThumbnailListWidget()
        listLayout.addWidget(self.listWidget)
        
        self.btnUp = QPushButton()
        self.btnUp.setIcon(QtGui.QIcon("./icons/Up.png"))
        self.btnDown = QPushButton()
        self.btnDown.setIcon(QtGui.QIcon("./icons/Down.png"))
        self.btnRemove = QPushButton()
        self.btnRemove.setIcon(QtGui.QIcon("./icons/Del.png"))
        self.btnAdd = QPushButton()
        self.btnAdd.setIcon(QtGui.QIcon("./icons/Add.png"))
        self.btnCopy = QPushButton()
        self.btnCopy.setIcon(QtGui.QIcon("./icons/Copy.png"))

        
        for btn in [self.btnUp, self.btnDown, self.btnRemove,self.btnCopy]:
            btn.setEnabled(False)
        
        self.btnUp.clicked.connect(self.moveUp)
        self.btnDown.clicked.connect(self.moveDown)
        self.btnRemove.clicked.connect(self.removeItem)
        self.btnAdd.clicked.connect(self.addItem)
        self.btnCopy.clicked.connect(self.copyItem)


        self.btnUp.setToolTip("Eins hoch")
        self.btnDown.setToolTip("Eins runter")
        self.btnRemove.setToolTip("Löschen")
        self.btnAdd.setToolTip("Hinzufügen Dialog")
        self.btnCopy.setToolTip("Kopieren")

        
        buttonLayout.addWidget(self.btnUp)
        buttonLayout.addWidget(self.btnDown)
        buttonLayout.addWidget(self.btnCopy)
        buttonLayout.addWidget(self.btnRemove)
        buttonLayout.addWidget(self.btnAdd)
        buttonLayout.addStretch()
        
        listButtonLayout.addLayout(listLayout)
        listButtonLayout.addLayout(buttonLayout)
        mainLayout.addLayout(listButtonLayout)        
        
        bottomLayout = QVBoxLayout()
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        bottomLayout.addWidget(separator)

        #statusbar above the buttons        
        self.statusbar = QtWidgets.QStatusBar(self)
        color = self.statusbar.palette().color(QtGui.QPalette.ColorRole.Window)
        darker = color.darker(150)
        lighter = color.darker(90)
        self.statusbar.setStyleSheet("QStatusBar { border: 1px inset %s; border-radius: 3px; background-color:%s;} "%(darker.name(),lighter.name()));
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setToolTip("Info und Fehler Anzeige")
        #bottomLayout.addWidget(self.statusbar)
        
        saveCancelLayout = QHBoxLayout()
        self.btnSave = QPushButton("Save")
        self.btnSave.setIcon(QtGui.QIcon("./icons/OK.png"))
        self.btnSave.setToolTip("Speichern & Ende")
        self.btnCancel = QPushButton("Cancel")
        self.btnCancel.setIcon(QtGui.QIcon("./icons/Del.png"))
        self.btnCancel.setToolTip("Ende")
        #saveCancelLayout.addStretch()
        saveCancelLayout.addWidget(self.statusbar)
        saveCancelLayout.addWidget(self.btnCancel)
        saveCancelLayout.addWidget(self.btnSave)
        bottomLayout.addLayout(saveCancelLayout)
        
        finalLayout = QVBoxLayout()
        finalLayout.addLayout(mainLayout)
        finalLayout.addLayout(bottomLayout)
        self.setLayout(finalLayout)
        
        self.listWidget.itemSelectionChanged.connect(self.updateButtons)
        self.btnSave.clicked.connect(self.saveList)
        self.btnCancel.clicked.connect(self.close)        
    
    def updateButtons(self):
        has_selection = bool(self.listWidget.selectedItems())
        self.btnUp.setEnabled(has_selection)
        self.btnDown.setEnabled(has_selection)
        self.btnRemove.setEnabled(has_selection)
        self.btnCopy.setEnabled(has_selection)
    
    def moveUp(self):
        row = self.listWidget.currentRow()
        if row > 0:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row - 1, item)
            self.listWidget.setCurrentItem(item)
    
    def moveDown(self):
        row = self.listWidget.currentRow()
        if row < self.listWidget.count() - 1:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row + 1, item)
            self.listWidget.setCurrentItem(item)
    
    def removeItem(self):
        row = self.listWidget.currentRow()
        if row >= 0:
            self.listWidget.takeItem(row)
    
    def addItem(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Auswahl", "", "Bilder & PDFs (*.png *.jpg *.jpeg *.bmp *.gif *.pdf)")
        if file_path:
            self.listWidget.addItemToList(file_path)
    
    def copyItem(self):
        row = self.listWidget.currentRow()
        item = self.listWidget.item(row).clone()
        #txt = item.text()
        #self.listWidget.addItemToList(txt)
        self.listWidget.insertItem(row - 1, item)        
    
    def saveList(self):
        #Save stuff to target. Display Message no buttons or progessbar...
        worker = LongRunningOperation(self.saveData)
        self.statusbar.showMessage("Die Daten werden zum Gerät gesendet...")
        worker.signal.connect(self._saveDone)
        # start the worker thread. 
        worker.startOperation() 


    def getErrorDialog(self, text, infoText, detailedText, mail=True):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        dlg.setWindowModality(Qt.WindowModality.WindowModal)
        dlg.setWindowTitle("Fehler")
        dlg.setText(text)
        dlg.setInformativeText(infoText)
        dlg.setDetailedText(detailedText)
        dlg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        spacer = QtWidgets.QSpacerItem(300, 1, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        layout = dlg.layout()
        layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())
        msg = infoText + "\n DETAIL:" + detailedText
        #if mail:
        #    self.model.mailError(msg)
        return dlg

#nice try from chat gpt, but is does not align with the parent...
'''
class WorkingDialog(QDialog):
    def __init__(self, parent: QWidget = None, message="Processing..."):
        super().__init__()
        self.setWindowTitle("Daten werden übertragen")
        #self.setWindowModality(Qt.WindowModality.ApplicationModal)  # Block other interactions
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setFixedSize(300, 120)
        
        layout = QVBoxLayout()

        # Info Icon
        self.icon_label = QLabel(self)
        #pixmap = QPixmap.fromTheme("dialog-information")  # Uses system icon
        icon = QIcon.fromTheme("dialog-information")
        pixmap = icon.pixmap(32, 32) if not icon.isNull() else QPixmap(32, 32)
        if pixmap.isNull():  # Fallback if no system icon
            pixmap.fill(Qt.GlobalColor.blue)
        self.icon_label.setPixmap(pixmap)

        # Message Label
        wrapped_message = "\n".join(textwrap.wrap(message, width=40))  # Wrap text
        self.message_label = QLabel(wrapped_message)        
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)
        self.setLayout(layout)
'''

''' Long running operations for actions that do not draw or paint '''        
class LongRunningOperation(QThread):
    signal = pyqtSignal(object) 

    def __init__(self, func, *args):
        QThread.__init__(self)
        self.function = func
        self.arguments = args
        self.msg=None

    def run(self):
        try:
            self.function(*self.arguments)
        except Exception as ex:
            Log.exception("***Error in LongRunningOperation***")
            self.msg = "Error while converting: "+str(ex)
        finally:
            self.signal.emit(self)

    def startOperation(self):
        self.start()  # invokes run - process pending QT events
        time.sleep(0.5)
        QCoreApplication.processEvents()


def getAppIcon():
    return QtGui.QIcon('./icons/filmstrip.png')

def handle_exception(exc_type, exc_value, exc_traceback):
    """ handle all exceptions """
    if WIN is not None:
        infoText = str(exc_value)
        detailText = "*".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        WIN.getErrorDialog("WTF Fehler", infoText, detailText).show()
        Log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

def parse():
    parser = argparse.ArgumentParser(description="AccessConfig")
    parser.add_argument('-d', dest="debug", action='store_true', help="Debug logs")
    parser.add_argument('-s', dest="server", type=str,default="beamer1", help="define which screen/beamer")
    return parser.parse_args() 

def main(args):
    if OSTools.checkIfInstanceRunning("Impresser"):
        print("App already running")
        sys.exit()
        
    try:
        global Log
        global WIN
        wd = OSTools.getLocalPath(__file__)
        OSTools.setMainWorkDir(wd)
        OSTools.setupRotatingLogger("Impresser", args.debug)
        Log = OSTools.Log
        if args.debug:
            OSTools.setLogLevel("Debug")
        else:
            OSTools.setLogLevel("Info")
        Log.info("--- Start Impresser ---")
        argv = sys.argv
        app = QApplication(argv)
        app.setWindowIcon(getAppIcon())
        device = args.server
        WIN = MainApp(app,device)  # keep python reference!
        app.exec()
    except:
        with open('/tmp/error.log', 'a') as f:
            f.write(traceback.format_exc())
        traceback.print_exc(file=sys.stdout)
        Log.exception("Error in main:")
        # ex_type, ex_value, ex_traceback
        sys_tuple = sys.exc_info()
        QtWidgets.QMessageBox.critical(None, "Error!", str(sys_tuple[1]))
    
            
if __name__ == "__main__":
    #app = QApplication(sys.argv)
    #app.setWindowIcon(getAppIcon())
    #window = MainApp()
    #window.show()
    #sys.exit(app.exec())
    sys.excepthook = handle_exception
    sys.exit(main(parse()))    
