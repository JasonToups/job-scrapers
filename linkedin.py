import pandas as pd
import re

from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from random import randint
from requests import get
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from time import time
start_time = time()

from variables import SEARCH_TERMS, LOCATION, GEOID, EXPERIENCE, TIMEFRAME, JOB_COUNT, regex, INCLUDE, EXCLUDE

# google stuff for google sheets implementation
import gspread
from gspread_dataframe import set_with_dataframe
gc = gspread.service_account()

from warnings import warn

def linkedin():
    # automatically for last week
    url = f"https://www.linkedin.com/jobs/search/?keywords={SEARCH_TERMS}&location={LOCATION}&geoid={GEOID}&f_E={EXPERIENCE}&f_TPR={TIMEFRAME}&sortBy=DD&f_TP=1%2C2&redirect=false&position=1&pageNum=0&f"

    # this will open up new window with the url provided above
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.get(url)
    sleep(3)
    action = ActionChains(driver)

    # to show more jobs. Depends on number of jobs selected
    i = 2
    while i <= (JOB_COUNT / 25): 
        try:
            driver.find_element(By.XPATH, '/html/body/main/div/section/button').click()
            sleep(5)
        except:
            break
        i = i + 1

    # parsing the visible webpage
    pageSource = driver.page_source
    lxml_soup = BeautifulSoup(pageSource, 'lxml')

    # searching for all job containers
    job_container = lxml_soup.find('ul', class_='jobs-search__results-list')
    job_listings = job_container.find_all('li', class_='result-card')
    print('You are scraping information about {} jobs.'.format(len(job_listings)))

    # setting up list for job information
    links = []
    post_title = []
    company_name = []
    post_date = []
    job_location = []
    job_desc = []

    # for loop for job title, company, id, location and date posted
    for job in job_listings:
        # job title
        job_title_element = job.find("span", attrs={"class": "screen-reader-text"})
        job_titles = job_title_element.text if job_title_element else None
        post_title.append(job_titles)

        # linkedin links
        job_ids = job.find('a', href=True)['href']
        job_ids = re.findall(r'(?!-)([0-9]*)(?=\?)', job_ids)[0]
        job_link = f"https://www.linkedin.com/jobs/search/?currentJobId={job_ids}&redirect=false"
        links.append(job_link)

        # company name
        company_name_element = job.select_one('img')
        company_names = company_name_element['alt'] if company_name_element else None
        company_name.append(company_names)

        # job location
        job_location_element = job.find("span", attrs={"class": "job-result-card__location"})
        job_locations = job_location_element.text if job_location_element else None
        job_location.append(job_locations)

        # posting date
        post_date_element = job.select_one('time')
        post_dates = post_date_element['datetime'] if post_date_element else None
        post_date.append(post_dates)

    # for loop for job description and criteria
    for x in range(1, len(links) + 1):
        # clicking on different job containers to view information about the job
        job_xpath = f'/html/body/main/div/section/ul/li[{x}]/img'
        driver.find_element(By.XPATH, job_xpath).click()
        sleep(3)

        # job description
        jobdesc_xpath = '/html/body/main/section/div[2]/section[2]/div'
        job_desc_element = driver.find_element(By.XPATH, jobdesc_xpath)
        job_descs = job_desc_element.text if job_desc_element else None
        job_desc.append(job_descs)

        # job criteria container below the description
        job_criteria_container = lxml_soup.find('ul', class_='job-criteria__list')
        all_job_criterias = job_criteria_container.find_all("span", class_='job-criteria__text job-criteria__text--criteria')

    # creating a dataframe
    exclude_job_data = pd.DataFrame({
        'Title': post_title,
        'Links': links,
        'Date': post_date,
        'Company Name': company_name,
        'Location': job_location,
        'Description': job_desc,
    })

    include_job_data = pd.DataFrame({
        'Title': post_title,
        'Links': links,
        'Date': post_date,
        'Company Name': company_name,
        'Location': job_location,
        'Description': job_desc,
    })

    # Convert all descriptions to strings
    exclude_job_data['Description'] = exclude_job_data['Description'].astype(str)
    include_job_data['Description'] = include_job_data['Description'].astype(str)

    # cleaning and filtering description column
    exclude_job_data['Description'] = exclude_job_data['Description'].str.replace('\n', ' ')
    include_job_data['Description'] = include_job_data['Description'].str.replace('\n', ' ')

    print('--- exclude data below ---')
    exclude_job_data = exclude_job_data[~exclude_job_data['Description'].str.contains(EXCLUDE, regex=True, case=False)]
    print(len(exclude_job_data.index))
    exlen = len(exclude_job_data.index)
    print('--- include data below ---')

    include_job_data = include_job_data[include_job_data['Description'].str.contains(INCLUDE, regex=True, case=False)]
    print(len(include_job_data.index))
    inlen = len(include_job_data.index)

    if inlen > 0 and exlen > 0:
        linkedin_data = pd.merge(exclude_job_data, include_job_data)
        print('--- merged data below ---')
    elif inlen == 0 and exlen > 0:
        linkedin_data = exclude_job_data
        print(f'using excluded filter only. cannot merge in: {inlen}, ex: {exlen}')
    elif inlen > 0 and exlen == 0:
        linkedin_data = include_job_data
        print(f'using included filter only. cannot merge inc: {inlen}, exc: {exlen}')
    else:
        linkedin_data = pd.DataFrame()  # Empty DataFrame instead of 0
        print('data not available or no jobs within parameter combo')

    if not linkedin_data.empty:
        print(linkedin_data.info())

    print(f"search includes {INCLUDE} and excludes {EXCLUDE}")

    return linkedin_data
