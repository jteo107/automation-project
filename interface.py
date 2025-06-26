from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from email.message import EmailMessage
load_dotenv()
import smtplib
import json
import pandas as pd
from datetime import datetime
import os
import sys
import time

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SPORTS_FILE = os.path.join(BASE_DIR, "sports.json")
with open(SPORTS_FILE, "r") as file:
    sports = json.load(file)

PREF_FILE = "preferences.json"
CONTACT_FILE = "contact.json"


def get_contact():
    print("Welcome to your personal sports news aggregator!\n Find the latest news from your favorite sports in one place.\n")
    time.sleep(3)
    contact = {}
    print("Please enter your email address: ")
    email = input("Email: ").strip()
    confirmed = False
    print(f"Confirm email: {email}")
    while(not confirmed):
        verify = input("Confirm (yes/no): ").strip().lower()
        if verify == "yes":
            contact['email'] = email
            confirmed = True
        else:
            print("Please enter your email address again: ")
            email = input("Email: ").strip()
            print(f"Confirm email: {email}")
            verify = input("Confirm (yes/no): ").strip().lower()
    with open("contact.json", "w") as file:
        json.dump(contact, file, indent=4)
    print("Contact information saved.")
    return contact

def load_contact():
    if(os.path.exists(CONTACT_FILE)):
        with open(CONTACT_FILE, "r") as file:
            contact = json.load(file)
            return contact
    else:
        return get_contact()


def get_preferences():
    preferences = {}
    global sports
    print("Available Sports: \n")
    for sport in sports:
        print(sport)
    print("Enter each sport you would like notifications about (STOP to stop)")
    while True:
        sport = input("Sport: ").strip().title()
        if sport == "Stop":
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
    app_path = os.getenv("APP_PATH")
    now = datetime.now()
##MMDDYYYY
    date = now.strftime("%m%d%Y")
    chromepath = os.getenv("CHROME_PATH")
    options = Options()
    options.headless = True
    service = Service(executable_path=chromepath)
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
     
def send_email(contact):
    email = contact['email']
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = email
    msg['Subject'] = "Your Daily Sports News!"
    body = "Today's Headlines and stories:\n\n"
    msg.set_content(body)
    app_path = os.getenv("APP_PATH")
    now = datetime.now()
    date = now.strftime("%m%d%Y")
    file_name = f'{date}--news.csv'
    final_path = os.path.join(app_path, file_name)

    if( os.path.exists(final_path)):
        with open(final_path,"rb") as file:
            file_content = file.read()
            file_name = os.path.basename(final_path)
            msg.add_attachment(file_content, maintype='text', subtype='csv', filename=file_name)
    else:
        msg.set_content("No news available for today. Please check back later.")
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
    server.quit()


if __name__ == "__main__":
    contact = load_contact()
    preferences = load_preferences()
    scrape(preferences)
    send_email(contact)
