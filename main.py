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
    indeed_data = indeed()
    angel_data = angel_list()

    if (linkedin_data is not None and indeed_data is not None and angel_data is not None):
        job_data = pd.concat([linkedin_data, indeed_data, angel_data], ignore_index=True)
        print('--- merged data below ---')
    elif (linkedin_data is None and indeed_data is not None and angel_data is not None):
        job_data = pd.concat([indeed_data, angel_data], ignore_index=True)
        # print(f'using excluded filter only. cannot merge in:{inlen}, ex: {exlen}')
    elif (linkedin_data is not None and indeed_data is None and angel_data is not None):
        job_data = pd.concat([linkedin_data, angel_data], ignore_index=True)
        # print(f'using included filter only. cannot merge inc:{inlen}, exc: {exlen}')
    elif (linkedin_data is not None and indeed_data is not None and angel_data is None):
        job_data = pd.concat([linkedin_data, indeed_data], ignore_index=True)
        # print(f'using included filter only. cannot merge inc:{inlen}, exc: {exlen}')
    else:
        job_data = pd.DataFrame()
        print('data not available or no jobs within parameter combo')

    if not job_data.empty:
        job_data.to_csv("jobs.csv", index=False)

run_scrapers()
