from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pandas as pd
from datetime import datetime
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREF_FILE = "preferences.json"
SPORTS_FILE = "sports.json"
with open(SPORTS_FILE, "r") as file:
    sports = json.load(file)

def get_preferences():
    print("Welcome to your personal sports news aggregator!\n Find the latest news from your favorite sports in one place.\n")
    time.sleep(3)
    preferences = {}
    global sports
    print("Available Sports: \n")
    for sport in sports:
        print(sport)
    print("Enter each sport you would like notifications about (STOP to stop)")
    while True:
        sport = input("Sport: ").strip()
        if sport == "stop" or sport == "STOP":
            break
        if sport in sports:
            preferences[sport] = {}
            print(f"{sport} added to your preferences.")
            leagues = sports[sport]
            print("Enter which leagues you would like notifications about (ALL for all leagues, STOP to stop, DISPLAY to see available leagues)")
            while True:
                league = input("League: ").strip()
                if league == "stop" or league == "STOP" or league == "Stop":
                    break
                if league == "display" or league == "DISPLAY" or league == "Display":
                    print(f"Available leagues for {sport}:")
                    for l in leagues:
                        print(l)
                if league == "all" or league == "ALL":
                    preferences[sport] = leagues
                    print(f"All leagues for {sport} added to your preferences.")
                    break
                elif league in leagues:
                    preferences[sport][league] = True
                    print(f"{league} added to your preferences for {sport}.")
        else:
            print("Invalid sport. Please try again.")
    with open(PREF_FILE, "w") as file:
        json.dump(preferences, file, indent=4)
    print("Preferences saved.")

    return preferences

def load_preferences():
    if(os.path.exists(PREF_FILE)):
        with open(PREF_FILE, "r") as file:
            preferences = json.load(file)
            return preferences
    else:
        return get_preferences()
    


def scrape(preferences):
    ##app_path = os.path.dirname(sys.executable)
    app_path = "/Users/Johann/sportsauto"
    now = datetime.now()
##MMDDYYYY
    date = now.strftime("%m%d%Y")
    path = "/Users/Johann/Downloads/chromedriver"
    options = Options()
    options.headless = True
    service = Service(executable_path=path)
    driver = webdriver.Chrome(service = service,options = options)
    titles = []
    links = []
    for i in preferences:
        if preferences[i] == {}:
            pass
        for league in preferences[i]:
            website = sports[i][league]['url']
            driver.get(website)
            waitforelement(driver, sports[i][league]['container_xpath'])
            containers = driver.find_elements(by = "xpath",value = sports[i][league]['container_xpath'])
            for j in containers:
                try:
                    title = j.find_element(by = "xpath", value = sports[i][league]['title_xpath']).text
                    link = j.find_element(by = "xpath", value = sports[i][league]['link_xpath']).get_attribute('href')
                    titles.append(title)
                    links.append(link)
                except Exception as e:
                    continue
    data_dict = {'title':titles,'link':links}
    data_headlines = pd.DataFrame(data_dict)
    file_name = f'{date}--news.csv'
    final_path = os.path.join(app_path,file_name)
    data_headlines.to_csv(final_path,index=False)
    driver.quit()
    return

def waitforelement(driver, xpath, timeout = 20):
     WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )



if __name__ == "__main__":
    preferences = load_preferences()
    scrape(preferences)
