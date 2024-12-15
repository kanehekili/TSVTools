'''
Created on Oct 28, 2024

@author: matze
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.support.wait import WebDriverWait
#from selenium.common.exceptions import TimeoutException
import time,io

from PIL import Image
    
'''
from selenium import webdriver

# Set up a Selenium WebDriver (e.g., using Chrome)
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode, without a UI
driver = webdriver.Chrome(options=options)

# Navigate to a page
driver.get("https://example.com")

# JavaScript is executed within the page, allowing interaction with JS-driven elements
element = driver.find_element_by_id("some-js-driven-element")

# Perform actions, like clicking a button that requires JavaScript
button = driver.find_element_by_id("button-id")
button.click()

# Get the page source after JavaScript has been executed
html = driver.page_source

# Do something with the HTML, then clean up
driver.quit()


we need Selenium -js has to be executed
?headless?
no

'''

def read1():
    '''
    Set up a Selenium WebDriver (e.g., using Chrome) on raspi...
    should work with 4.10.0 OOTB
    '''
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # Run in headless mode, without a UI
    options.add_argument("--enable-javascript")
    driver = webdriver.Chrome(options=options)
    
    # Navigate to a page
    #driver.get("http://192.168.178.9/start_teq.svgz#%23SC_View_001")
    driver.get("http://192.168.178.9")
    # JavaScript is executed within the page, allowing interaction with JS-driven elements
    #element = driver.find_element(By.ID,"SC_View_001")
    #elements = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    #elements = driver.execute_script("return document.getElementsByTagName('svg')") #leer
    #elements = WebDriverWait(driver, 100).until(lambda x: x.find_element(By.TAG_NAME, "svg"))
    '''
    we do not know when this construct is done painting... So we need to sleep
    try:
        WebDriverWait(driver, 20).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete")
    except TimeoutException as err:
        print("Page not loaded",err)    
    '''
    time.sleep(20)
    driver.set_window_rect(width=500, height=500)
    dic= driver.get_window_rect()
    print(dic)
    #driver.save_screenshot("hugo.png")
    rawImg = driver.get_screenshot_as_png()
    img = Image.open(io.BytesIO(rawImg))
    #time.sleep(1)
    #img = Image.open("hugo.png")
    colors=[]
    limit = 3*255
    colors.append(img.getpixel((226,286)))
    colors.append(img.getpixel((223,291)))
    colors.append(img.getpixel((230,291)))
    for pick in colors:
        if pick[0]+pick[1]+pick[2] < limit:
            print("Error or warning:",pick)
            break
        else:
            print("check ok:",pick)
    
    '''
    JS must be executed! - No chance, because SVG is doing its own stuff.
    '''
    #elements = driver.execute_script("return document.body.innerHTML")
    #elements = driver.execute_script("start_teq.svgz#%23SC_View_001")
    #elements = driver.execute_script("http://192.168.178.9/start_teq.svgz#%23SC_View_001")
    #start_teq.svgz
    # Perform actions, like clicking a button that requires JavaScript
    #button = driver.find_element_by_id("button-id")
    #button.click()
    
    # Get the page source after JavaScript has been executed
    #html = driver.page_source
    #print(elements)
    
    # Do something with the HTML, then clean up
    driver.quit()
    print("done")

if __name__ == '__main__':
    read1()
    pass