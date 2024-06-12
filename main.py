import pandas as pd
from linkedin import linkedin
from indeed import indeed
from angel_list import angel_list
from variables import SEARCH_TERMS, LOCATION, JOB_COUNT, regex, INCLUDE, EXCLUDE

class Parameters:
    def __init__(self, search_terms, location, job_count, include, exclude) -> None:
        self.search_terms = search_terms
        self.location = location
        self.job_count = job_count
        self.include = include
        self.exclude = exclude

def run_scrapers():
    linkedin_data = linkedin()
    
    if (linkedin_data is not None):
        job_data = pd.concat([linkedin_data], ignore_index=True)
        print('--- merged data below ---')
    else:
        job_data = pd.DataFrame()
        print('data not available or no jobs within parameter combo')

    if not job_data.empty:
        job_data.to_csv("linkedin-jobs.csv", index=False)

run_scrapers()
