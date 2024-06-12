import pandas as pd
import re

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep, time
start_time = time()

from variables import SEARCH_TERMS, LOCATION, JOB_COUNT, INCLUDE, EXCLUDE

# Google stuff for Google Sheets implementation
import gspread
from gspread_dataframe import set_with_dataframe
gc = gspread.service_account()

def indeed():
    url = f"https://www.indeed.com/jobs?q={SEARCH_TERMS}&l={LOCATION}&limit={JOB_COUNT}"

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.get(url)
    sleep(5)  # Increased sleep time

    # Parsing the visible webpage
    pageSource = driver.page_source
    soup = BeautifulSoup(pageSource, 'lxml')

    # Searching for all job containers
    job_container = soup.find_all('div', class_='jobsearch-SerpJobCard')
    print('You are scraping information about {} jobs.'.format(len(job_container)))

    # Setting up list for job information
    links = []
    post_title = []
    company_name = []
    post_date = []
    job_location = []
    job_desc = []

    for job in job_container:
        job_title_element = job.find("h2", attrs={"class": "title"})
        job_titles = job_title_element.text.strip() if job_title_element else None
        post_title.append(job_titles)

        job_ids = job.find('a', href=True)['href']
        job_link = f"https://www.indeed.com{job_ids}"
        links.append(job_link)

        company_name_element = job.find('span', attrs={"class": "company"})
        company_names = company_name_element.text.strip() if company_name_element else None
        company_name.append(company_names)

        job_location_element = job.find("div", attrs={"class": "recJobLoc"})
        job_locations = job_location_element['data-rc-loc'] if job_location_element else None
        job_location.append(job_locations)

        post_date_element = job.find('span', attrs={"class": "date"})
        post_dates = post_date_element.text.strip() if post_date_element else None
        post_date.append(post_dates)

    for link in links:
        driver.get(link)
        sleep(3)

        job_desc_element = driver.find_element(By.ID, 'jobDescriptionText')
        job_descs = job_desc_element.text if job_desc_element else None
        job