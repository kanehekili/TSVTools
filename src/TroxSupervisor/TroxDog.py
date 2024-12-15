'''
Created on Dec 8, 2024

@author: matze
 pip install selenium --break-system-packages
pacman -Syu python-pillow chromium or firefox (yes we need a browser)
firefox seems to be much faster..
'''
import signal,sys
sys.path.append('/home/matze/git/TSVAccess/src')

# sys.path.append('/opt/tsvserver/')
from selenium import webdriver
import io,time
from PIL import Image
from threading import Event
import DBTools
from TsvDBCreator import DBAccess
from DBTools import OSTools
#---
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

OSTools.setupRotatingLogger("TroxDog", True)
Log = DBTools.Log
DaemonEvt=Event()

#RECEIPIENTS = ["mathias.wegmann@tsv-weilheim.com","Manuel.Schoepf@tsv-weilheim.com"]#Thysah won't work
RECEIPIENTS = ["mathias.wegmann@tsv-weilheim.com"] #While testin
DEFER_SNAPSHOT=10 #Wait time secs until analyzing

class Watchdog():
    INTERVAL=15*60 #15 Minutes
    URL="http://192.168.178.9"
    MODE_OK=0
    MODE_WARN=1
    MODE_ERROR=2
    def __init__(self,debug=False):
        if not debug:
            OSTools.setLogLevel("Info")        
        self.scraper = Scraper(DaemonEvt)
        self.mode = Watchdog.MODE_OK 
        self.running = True
        self.connect()
    
    def connect(self):
        self.dbSystem=DBAccess()
        self.db = self.dbSystem.connectToDatabase()
        if not self.db.isConnected():
            self.shutDown(9, None)
        #TODO self healing... 
        
    def runDeamon(self):
        while self.running:
            try:
                Log.info("Check url")
                rawImg = self.scraper.imageOfURL(Watchdog.URL)
                result = self.analyze(rawImg)
                if result:
                    self.mailError(result)   
                else:
                    if self.mode != self.MODE_OK:
                        Log.info("Resetting Error message - self healing")
                    self.mode=self.MODE_OK 
            except KeyboardInterrupt:
                Log.warnig("Exit keyinterrupt")
                return
            except Exception as ex:
                Log.error("Error while parsing:%s", str(ex), exc_info=1)
            Log.info("Pending...")
            DaemonEvt.wait(Watchdog.INTERVAL)
        Log.info("Stopping daemon...")    

    def mailError(self,attachment):
        if self.mode == self.MODE_OK:
            Log.warning("Error - sending email")
            self.mode = self.MODE_ERROR
            msg = "Eine Fehlermeldung wurde auf der TROX Anlage entdeckt. Im Anhang kann die Meldung analysiert werden. Weitere Infos unter der Adresse %s (ggf WireGuard!)"%(self.URL)
            subject = "Meldung Trox Lüftung Nordbau"
            self.dbSystem.genericEmail(self.db, subject, msg, RECEIPIENTS,attachment)
        else:
            Log.info("Error reoccurred - refrainig from spamming")
    
    def analyze(self,rawImage):
        rawBuffer= io.BytesIO(rawImage)
        img = Image.open(rawBuffer)
        colors=[]
        limit = 3*255
        colors.append(img.getpixel((226,286)))
        colors.append(img.getpixel((223,291)))
        colors.append(img.getpixel((230,291)))
    
        #test on error
        timestr = time.strftime("%Y-%m-%d-%H%M%S")
        fn = "trox"+timestr+".png"
        #img.save("trox"+timestr+".png")
        return (rawBuffer,fn)
    
        for pick in colors:
            if pick[0]+pick[1]+pick[2] < limit:
                Log.warning("Error detected:%s",pick)
                return (rawBuffer,fn)
            else:
                Log.debug("Check ok:%s",pick)
        return None

    def shutDown(self,signo, _frame):
        Log.warning("Interrupted by %d, shutting down",signo)
        self.running=False
        DaemonEvt.set()
        


class Scraper():
    def __init__(self,threadingEvent):
        '''
        Set up a Selenium WebDriver (e.g., using Chrome) on raspi...
        should work with 4.10.0 OOTB
        '''
        #options = webdriver.ChromeOptions()
        #options.add_argument('--headless=new')  # Run in headless mode, without a UI
        #options.add_argument("--enable-javascript")
        #self.driver = webdriver.Chrome(options=options)
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)     
        self.actions = ActionChains(self.driver)   
        self.threadingEvent = threadingEvent
    
    def imageOfURL(self,url):
        self.driver.get(url)
        #we do not know when this construct is done painting... So we need to sleep
        self.threadingEvent.wait(10)
        self.driver.set_window_rect(width=500, height=500)
        self.actions.move_by_offset(223,291).click().perform()
        self.threadingEvent.wait(5)
        rawImg = self.driver.get_screenshot_as_png()
        return rawImg

if __name__ == '__main__':
    argv = sys.argv
    w = Watchdog(False)
    signal.signal(signal.SIGTERM, w.shutDown)
    signal.signal(signal.SIGINT, w.shutDown)
    signal.signal(signal.SIGHUP, w.shutDown)  

    w.runDeamon()
