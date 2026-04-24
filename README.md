Automated Sports News Aggregator Project

Project Description:

This project is a custom sports news aggregator that prompts a user for their favorite sports and corresponding sports leagues. The aggregator is written in Python, and utilizes Selenium WebDriver to scrape a selection of websites for news headlines and links. It then emails the aggregated headlines and website links in a text file to the user using the SMTP Library, and performs this task daily using Cron to automate the task. After prompting the user and collecting the user's preferences, the user's preferences are saved to a JSON file and used for future execution without needing to prompt the user every day. This is a personal project done mostly to force myself to work on projects outside of my comfort zone and outside of my usual area of focus. 

How to Install and Run:

1. Clone Repository
2. Run pyinstaller --onefile interface.py in terminal
3. Run ./dist/interface

Languages, Libraries, and Tools:
- Python
- Selenium Webdriver
- Cron
- JSON
- Pandas
- smtpLib


