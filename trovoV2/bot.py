from selenium import webdriver as uc
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import random
import os
import time
import multiprocessing
import pickle
import configparser

def Main():

    WelcomeMessage()
    StepSelector()
    config = Configurator()
    cookies = GetCookies(int(config["number_of_viewers"]))
    print("[INFO] Cookies chosen:",cookies)
    proxies = GetProxies(int(config["number_of_viewers"]))
    print("[INFO] Proxies chosen:",proxies)
    bots = 0
    for i in range(int(config["number_of_viewers"])):
        if int(config["chat_enabled"]) == 1:
            process = multiprocessing.Process(target=BotLogic,args=[proxies[i],cookies[i],1,config["stream_link"]])
        else:
            process = multiprocessing.Process(target=BotLogic,args=[proxies[i],cookies[i],0,config["stream_link"]])
        process.start()
        bots+=1
        print("[INFO] Bots started: ",bots)
        time.sleep(random.uniform(int(config["join_time_minimum"]),int(config["join_time_maximum"])))
    input("[INFO] Done. Press enter to shut down the bots.")

def WelcomeMessage():
    os.system("cls")
    print("Trovo viewBOTv2 - By: 0xDEAD team.")
def StepSelector():
    print("\nPlease select an option from below:\n")
    selection = input("start: Starts the bot.\nconfig: launches the configurator.\n$ ")
    if selection.lower() == "start":
        return
    elif selection.lower()=="config":
        SettingsConfigurator()

def SettingsConfigurator():
    os.system("cls")
    print("[INFO] Welcome to the configurator. Here you will configure your BOT.")
    config = configparser.ConfigParser()
    config["LINKS"] = {}
    config["LINKS"]["stream_link"] = input("Enter the stream link:\n$ ")
    config["LINKS"]["diversion_link"] = "https://trovo.live/"
    config["VIEWERS"] = {}
    config["VIEWERS"]["number_of_viewers"] = input("Number of bots you wish to have?\n$ ")
    config["VIEWERS"]["search_tearm"] = input("Channel name (used for the search term)?\n$ ")
    config["VIEWERS"]["chat_enabled"] = input("Should bots chat? (1 yes,0 no.)?\n$ ")
    config["VIEWERS"]["join_time_minimum"] = input("Minimum time to wait before adding a new viewer?\n$ ")
    config["VIEWERS"]["join_time_maximum"] = input("Maximum time to wait before adding a new viewer?\n$ ")

    with open("configuration.ini","w+") as f:
        config.write(f)

#                                                                                                           BOT LOGIC

def BotLogic(proxy,cookie,chatEnabled=0,URL="https://www.trovo.live/",DIV_URL="https://www.trovo.live/"):
    options = uc.ChromeOptions()
    options.add_argument(f"--proxy-server={proxy}")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--disable-application-cache")
    options.headless = True
    options.add_argument("--log-level=3")
    options.add_argument("--mute-audio")

    driver = uc.Chrome(options=options)
    SetWindowSize(driver)
    try:
        driver.get(DIV_URL)
    except:
        print("[!] Error when opening URL.")
        driver.quit()
        time.sleep(5)
        process = multiprocessing.Process(target=BotLogic,args=[GetProxies(1)[0],cookie,URL])
        process.start()
        return -1
    if CheckFor403Error(driver) == 0:
        pass
    else:
        driver.quit()
        time.sleep(5)
        process = multiprocessing.Process(target=BotLogic,args=[GetProxies(1)[0],cookie,URL])
        process.start()
        quit()
    if InjectCookie(cookie,driver) == 0:
        pass
    else:
        quit()

    time.sleep(5)
    possibleWaysToEnter = [EnterByURL,EnterBySearch]
    possibleWaysToEnter[random.randint(0,len(possibleWaysToEnter)-1)](driver)
    time.sleep(5)
    PressPlayButton(driver)
    time.sleep(5)
    PressOkayForChat(driver)
    while True:
        RandomEvents(driver,cookie,chatEnabled)
        time.sleep(random.uniform(300,500))
    print("[G] Process finished. Quitting.")
    driver.quit()
    quit()
#                                                                                                            END BOT LOGIC

def GetProxies(ammount):
    #Returns random proxies.
    proxies = []
    with open("proxyList.txt",'r') as f:
        temp = f.readlines()
        tempProxies = [line.rstrip() for line in temp]
    for i in range(ammount):
        randomNumber = random.randint(0,len(tempProxies)-1)
        proxies.append(tempProxies[randomNumber])
        del tempProxies[randomNumber]
        
    return proxies
def GetCookies(ammount):
    #Returns random cookies.
    cookies = []
    tempCookies = []
    try:
        for root, dirs,files in os.walk("active_cookies"):
            for file in files:
                tempCookies.append(file)
        for i in range(ammount):
            ran = random.randint(0,len(tempCookies)-1)
            cookies.append(tempCookies[ran])
            del tempCookies[ran]
    except Exception as e:
        print(e)
    return cookies
def GetChatMessages():
    with open(os.path.join("bot_chat","")+"poruke.txt",'r') as f:
        wm = f.readlines()
        wm = [line.rstrip() for line in wm]
    return wm
def InjectCookie(cookie,driver):
    try:
        with open(os.path.join("active_cookies","")+cookie,'rb') as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                if 'sameSite' in cookie:
                    if cookie["sameSite"] == 'None':
                        cookie["sameSite"] = "Strict"
                driver.add_cookie(cookie)
            time.sleep(2)
        return 0
    except:
        print("[!] Could not inject cookies")
        return -1
def CheckFor403Error(driver):
    try:
        element = driver.find_element(By.XPATH,"/html/body/h1")
        if element.text == "403 Forbidden":
            print("[!] Proxy has been flagged as dead. Stopping and choosing another proxy.")
            return -1
    except:
        print("[G] Proxy is working correctly.")
        return 0
def SetWindowSize(driver):
    driver.set_window_size(random.uniform(1200,1920),random.uniform(800,1080))

def Configurator():
    cnf = {}
    config = configparser.ConfigParser()
    config.read("configuration.ini")
    cnf["stream_link"]= config["LINKS"]["stream_link"]
    cnf["diversion_link"]=config["LINKS"]["diversion_link"]
    cnf["number_of_viewers"] = config["VIEWERS"]["number_of_viewers"]
    cnf["chat_enabled"] = config["VIEWERS"]["chat_enabled"]
    cnf["join_time_minimum"] = config["VIEWERS"]["join_time_minimum"]
    cnf["join_time_maximum"] = config["VIEWERS"]["join_time_maximum"]
    return cnf

    
def RandomEvents(driver,cookie,chatEnabled):
    succeeded = False
    if "burner" in cookie.lower():
        print("[G]", cookie ,"alive.")
        return True
    possibleEvents = [CastSpell,ClickChatSettings,FollowChannel,SendChatMessage]
    randomNumber = random.randint(0,len(possibleEvents)-1)
    if randomNumber>len(possibleEvents)-2:
        if chatEnabled == 1:
            succeeded=possibleEvents[randomNumber](driver,GetChatMessages())
    else:
        succeeded=possibleEvents[randomNumber](driver)
    while succeeded!=True:
        randomNumber = random.randint(0,len(possibleEvents)-1)
        if randomNumber>len(possibleEvents)-2:
            if chatEnabled == 1:
                succeeded=possibleEvents[randomNumber](driver,GetChatMessages())
        else:
            succeeded=possibleEvents[randomNumber](driver)
    return succeeded
def CastSpell(driver):
    try:
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/button")
        time.sleep(2)
        element.click()
        time.sleep(2)
        try:
            element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div[4]/article/div[1]/div[1]/ul/li[1]/div")
            hover = ActionChains(driver).move_to_element(element)
            time.sleep(2)
            hover.perform()
        except:
            print("[!] Hovering over mana spell failed.")
        time.sleep(5)
        element.click()
        try:
            element = driver.find_element(By.CSS_SELECTOR,"#gift_520010002 > button")
            element.click()
        except:
            print("[?] Account is verified already.")
        time.sleep(1)
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/button")
        time.sleep(2)
        element.click()
        print("[G] Mana has been sent successfully.")
        return True
    except Exception as e:
        print("[!] Error when casting a spell.")
        return False
def FollowChannel(driver):
    try:
        element = driver.find_element(By.CSS_SELECTOR,"#live-fullscreen > div.anchor-box > section > div.feature-wrap > button.cat-button.cat-f-btn.normal.primary > span.text")
        if element.text == "Follow":
            element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[5]/section/div[2]/button[3]")
            element.click()
        else:
            print("[G] Channel is already being followed.")
    except:
        print("[G] Channel is already being followed.")
def ClickChannelAndGoBack(driver):
    try:
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[1]/div[1]/div[3]/div[1]/div/a[1]/div[1]/img")
        time.sleep(0.1)
        element.click()
        time.sleep(random.uniform(120,300))
        driver.back()
        return True
    except:
        print("[!] Error when clicking another channel.")
        return False

def ClickChatSettings(driver):
    try:
        time.sleep(random.uniform(2,5))
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[2]/div/section/div[3]/div/section/div[1]/div[2]/button[2]")
        element.click()
        time.sleep(random.uniform(2,5))
        element.click()   
        return True
    except:
        print("[!] Error when clicking chat settings.")
        return False
def SendChatMessage(driver,chat_messages):
    try:
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[2]/div/section/div[3]/div/section/div[1]/div[1]/div[1]")
        chat_messages = chat_messages[random.randint(0,len(chat_messages)-1)]
        if ':' not in chat_messages :
            for i in chat_messages:
                time.sleep(random.uniform(0.1,0.5))
                element.send_keys(i)
            element.send_keys(Keys.ENTER)
            return True
        else:
            for i in chat_messages:
                time.sleep(random.uniform(0.1,0.5))
                element.send_keys(i)
            element.send_keys(Keys.ENTER)  
            time.sleep(0.2)
            element.send_keys(Keys.ENTER)
            print("[G] Chat message sent successully.")
            return True
    except Exception as e:
        print("[!] There was an error sending a chat message.")
        return False
def PressPlayButton(driver):
    try:
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[3]/div/section[2]/button[1]")
        time.sleep(2)
        element.click()
    except:
        print("[?] Missing allow cookies. Assuming that there was no such button. Continuing...")
    try:
        try:
            element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div[5]/div[3]/section/div/button[2]")
            time.sleep(2)
            element.click()
        except:
            print("[?] Missing continue watching, assuming channel is family friendly. Continuing...")
        time.sleep(random.uniform(1,10))
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div[2]/div[9]/div[4]/div[1]")
        time.sleep(random.uniform(1,3))
        element.click()
       
    except:
        print("[?] Play button was not found. Continuing...")
def PressOkayForChat(driver):
    try:
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[2]/div/section/div[3]/div/section/section/div/button")
        element.click()
    except:
        print("[?] There was no \"Got it!\" button. Continuing.")
def EnterByURL(driver):
    config = configparser.ConfigParser()
    config.read("configuration.ini")
    URL = config["LINKS"]["stream_link"]
    driver.get(URL)
def EnterBySearch(driver):
    driver.refresh()
    time.sleep(5)
    config = configparser.ConfigParser()
    config.read("configuration.ini")
    toType = config["VIEWERS"]["search_tearm"]
    print("[INFO] Entering stream by search.")
    try:
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/nav/div[2]/div/input")
        for i in toType:
            element.send_keys(i)
            time.sleep(random.uniform(0.1,0.5))
        element.send_keys(Keys.ENTER)
    except:
        print("[!] Error while searching for channel.")
        driver.quit()
    time.sleep(5)
    driver.set_page_load_timeout(200)
    try:
        element = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[1]/div[2]/div/ul/li[1]/div/div/a")
        element.click()
    except:
        print("[!] Could not find channel, entering by URL instead.")
        EnterByURL(driver)
        driver.quit()
if __name__ == "__main__":  
    multiprocessing.freeze_support()
    Main()
