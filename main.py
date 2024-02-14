import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters, IndustryFilters, OnSiteOrRemoteFilters
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime
import re

# Change root logger level (default is WARN)
logging.basicConfig(level=logging.INFO)

# Fired once for each successfully processed job
# Create an empty DataFrame
df = pd.DataFrame(columns=['Title', 'Company','Place' , 'Date', 'Link', 'Experience','Stack', 'Description','Applied'])

# Fired once for each successfully processed job
def on_data(data: EventData):
    global df
    
    # List of keywords to search for in the description
    keywords = ['python', 'react', 'javascript','django']
    ignore = ['php','.net','c#','c++','linux']
    # Find which keywords are in the description
    found_keywords = [keyword for keyword in keywords if keyword in data.description.lower()]
    ignore_keywords = [keyword for keyword in ignore if keyword in data.description.lower()]
    
    # Extract years of experience from the description
    experience_matches = re.findall(r'(\d+)\s*years?\s*(of)?\s*experience', data.description.lower())
    experience = int(experience_matches[0][0]) if experience_matches else None

    # Append data to the DataFrame only if any of the keywords is in the description
    if found_keywords and not ignore_keywords:
        new_row = pd.DataFrame({
            'Title': [data.title], 
            'Company': [data.company], 
            'Place': [data.place], 
            'Date': [data.date], 
            'Link': [data.link], 
            'Experience': [experience],
            'Stack': [', '.join(found_keywords)], 
            'Description': [data.description],
            'Applied': [False],
        })
        df = pd.concat([df, new_row], ignore_index=True)
        print('[ON_DATA]', data.title, data.company)

# Fired when all the scraping jobs are done
def on_end():
    print('[ON_END]')
    global df
    
    # Get current date
    current_date = datetime.now().strftime('%Y_%m_%d')
    
    # File path
    file = f'linkedin_jobs_{current_date}.xlsx'
    
    # Try to open an existing workbook
    try:
        existing_df = pd.read_excel(file)
        combined_df = pd.concat([df, existing_df], ignore_index=True)
        combined_df.drop_duplicates(subset=['Title', 'Company', 'Place'], keep='first', inplace=True)

        # Write the combined DataFrame to a new Excel file with the same name
        combined_df.to_excel(file, index=False)

    except FileNotFoundError:
        # File does not exist yet, we will create it
        df.to_excel(file, index=False)

# Fired once for each page (25 jobs)
def on_metrics(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))


def on_error(error):
    print('[ON_ERROR]', error)

scraper = LinkedinScraper(
    chrome_executable_path=None,  # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
    chrome_binary_location=None,  # Custom path to Chrome/Chromium binary (e.g. /foo/bar/chrome-mac/Chromium.app/Contents/MacOS/Chromium)
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=1.3,  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
    page_load_timeout=1000,  # Page load timeout (in seconds)    
    
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [

    Query(
        query='Junior Software Developer',
        options=QueryOptions(
            locations=['London, England, United Kingdom','United Kingdom',],  # Locations to scrape
            apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
            skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
            limit=1000,
            filters=QueryFilters(               
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.DAY,
                type=[TypeFilters.FULL_TIME],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL],
            )
        )
    ),
    Query(
        query='Software Developer',
        options=QueryOptions(
            locations=['London, England, United Kingdom','United Kingdom',],  # Locations to scrape
            apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
            skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
            limit=1000,
            filters=QueryFilters(               
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.DAY,
                type=[TypeFilters.FULL_TIME],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL],
            )
        )
    ),
    Query(
        query='Developer',
        options=QueryOptions(
            locations=['London, England, United Kingdom','United Kingdom',],  # Locations to scrape
            apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
            skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
            limit=1000,
            filters=QueryFilters(               
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.DAY,
                type=[TypeFilters.FULL_TIME],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL],
            )
        )
    ),
]

scraper.run(queries)