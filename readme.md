## Job Search Web Scrapers

These are some open projects pieced together from tutorials to help with the job search.

Currently attempting to automatically eliminate content, change the csv to write to google sheets, by row if necessary and schedule using airflow.

This was pushed up for GA alumni colabbing

This is worked on in my off time, so not that often.

## Use a Python Environment

If you use Conda to set your Python version for this project, then run this:

```shell
conda update python
```

## Install Dependencies

```shell
pip install -r requirements.txt
```

## Working with Google Sheets API Credentials

The output of the Job Search will go to Google Sheets for application tracking.

To download the JSON file containing your credentials for Google Sheets API (or any Google API) through the Google Cloud Platform, follow these steps:

1. **Access Google Cloud Console**:

   - Visit the [Google Cloud Console](https://console.developers.google.com/) and log in with your Google account.

2. **Select or Create a Project**:

   - If you haven't already, create a new project by clicking on the "New Project" button at the top right corner. Fill in the project details and create it.
   - If you have an existing project, select it from the project dropdown at the top of the page.

3. **Enable the Google Sheets API**:

   - Navigate to the "APIs & Services > Dashboard" section.
   - Click on "+ ENABLE APIS AND SERVICES" at the top.
   - Search for "Google Sheets API", select it, and click "Enable".

4. **Create Credentials**:

   - After enabling the API, go to the "Credentials" tab on the left sidebar.
   - Click on "Create Credentials" at the top of the page and select "Service account".
   - Fill in the service account details. You can give it any name and description.
   - Click "Create" and then "Continue" until you reach the "Grant users access to this service account" screen, then click "Done".

5. **Generate the JSON Key**:

   - After creating the service account, you'll be redirected to the "Credentials" page where your new service account will be listed.
   - Click on the email address of the service account you just created.
   - Go to the "Keys" tab.
   - Click on "Add Key" and choose "Create new key".
   - Select "JSON" as the key type and click "Create".
   - The JSON key file will be automatically downloaded to your computer.

6. **Secure Your Key**:
   - Rename your credentials file to `service_account.json`
     - This JSON file contains sensitive information that allows access to your Google Sheets under the permissions you've set. Keep it secure and do not share it publicly.
   - Place the downloaded `credentials.json` file in the directory `/Users/{user}/.config/gspread/`.

After downloading the JSON file, you can use it in your project to authenticate with Google Sheets API by referencing it in your code, as needed.
