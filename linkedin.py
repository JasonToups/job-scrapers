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

from variables import SEARCH_TERMS, LOCATION, GEOID, EXPERIENCE, TIMEFRAME, PP, POSITION, PAGE_NUM, JOB_COUNT, INCLUDE, EXCLUDE

# Google stuff for Google Sheets implementation
import gspread
from gspread_dataframe import set_with_dataframe
gc = gspread.service_account()

def linkedin():
    url = f"https://www.linkedin.com/jobs/search/?keywords={SEARCH_TERMS}&location={LOCATION}&geoid={GEOID}&f_E={EXPERIENCE}&f_TPR={TIMEFRAME}&f_PP={PP}&position={POSITION}&pageNum={PAGE_NUM}"

    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.get(url)
    sleep(5)  # Increased sleep time

    # to show more jobs. Depends on number of jobs selected
    i = 2
    while i <= (JOB_COUNT / 25): 
        try:
            more_jobs_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "See more jobs")]')
            more_jobs_button.click()
            sleep(5)  # Increased sleep time
        except Exception as e:
            print(f"Error clicking 'Show More Jobs' button: {e}")
            break
        i += 1

    # parsing the visible webpage
    pageSource = driver.page_source
    lxml_soup = BeautifulSoup(pageSource, 'lxml')

    # Searching for all job containers
    job_container = lxml_soup.find('ul', class_='jobs-search__results-list')
    if not job_container:
        print("Job container not found.")
        return pd.DataFrame()  # Return empty DataFrame
    
    job_listings = job_container.find_all('li')
    print(f'Found job listings: {len(job_listings)}')

    # Setting up list for job information
    links = []
    post_title = []
    company_name = []
    post_date = []
    job_location = []
    job_desc = []

    for job in job_listings:
        job_title_element = job.find("h3", class_="base-search-card__title")
        job_titles = job_title_element.text.strip() if job_title_element else None
        post_title.append(job_titles)

        job_id_element = job.find('a', href=True)
        if job_id_element:
            job_id = job_id_element['href']
            job_id_match = re.search(r'/jobs/view/(\d+)', job_id)
            print(job_id)
            print(job_id_match)
            if job_id_match:
                job_id = job_id_match.group(1)
                job_link = f"https://www.linkedin.com/jobs/view/{job_id}/"
                links.append(job_link)
            else:
                links.append(None)
        else:
            links.append(None)

        company_name_element = job.find('h4', class_='base-search-card__subtitle')
        company_names = company_name_element.text.strip() if company_name_element else None
        company_name.append(company_names)

        job_location_element = job.find("span", class_="job-search-card__location")
        job_locations = job_location_element.text.strip() if job_location_element else None
        job_location.append(job_locations)

        post_date_element = job.find('time')
        post_dates = post_date_element['datetime'] if post_date_element else None
        post_date.append(post_dates)

    print(f'Collected {len(post_title)} job titles, {len(links)} links, {len(company_name)} company names, {len(job_location)} job locations, {len(post_date)} post dates')

    for x in range(1, len(links) + 1):
        job_xpath = f'//ul[@class="jobs-search__results-list"]/li[{x}]//a'
        driver.find_element(By.XPATH, job_xpath).click()
        sleep(3)

        jobdesc_xpath = '//section[contains(@class, "description")]'
        job_desc_element = driver.find_element(By.XPATH, jobdesc_xpath)
        job_descs = job_desc_element.text if job_desc_element else None
        job_desc.append(job_descs)

    print(f'Collected {len(job_desc)} job descriptions')

    # Ensure all lists are of the same length
    min_length = min(len(post_title), len(links), len(company_name), len(post_date), len(job_location), len(job_desc))
    post_title = post_title[:min_length]
    links = links[:min_length]
    company_name = company_name[:min_length]
    post_date = post_date[:min_length]
    job_location = job_location[:min_length]
    job_desc = job_desc[:min_length]

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

    exclude_job_data['Description'] = exclude_job_data['Description'].astype(str)
    include_job_data['Description'] = include_job_data['Description'].astype(str)

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
        linkedin_data = pd.DataFrame()
        print('data not available or no jobs within parameter combo')

    if not linkedin_data.empty:
        print(linkedin_data.info())

    print(f"search includes {INCLUDE} and excludes {EXCLUDE}")

    return linkedin_data