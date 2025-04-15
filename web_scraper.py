import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import datetime
import os  # ← THIS was missing
import schedule
import time


# Logging setup
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def scrape_jobs():
    print("Starting scraping process...")
    url = "https://vacancymail.co.zw/jobs/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        job_cards = soup.select(".job-listing")
        if not job_cards:
            print("No job listings found.")
            return

        job_data = []

        for job in job_cards[:10]:  # Limit to top 10 jobs
            title = job.select_one(".job-listing-title").text.strip() if job.select_one(".job-listing-title") else "N/A"
            company = job.select_one(".job-listing-company").text.strip() if job.select_one(".job-listing-company") else "N/A"
            location = job.select_one(".icon-material-outline-location-on").find_next('li').text.strip() if job.select_one(".icon-material-outline-location-on") else "N/A"
            expiry = job.select_one(".icon-material-outline-access-time").find_next('li').text.strip() if job.select_one(".icon-material-outline-access-time") else "N/A"
            description = job.select_one(".job-listing-text").text.strip() if job.select_one(".job-listing-text") else "N/A"

            job_data.append({
                "Title": title,
                "Company": company,
                "Location": location,
                "Expiry Date": expiry,
                "Description": description
            })

        df = pd.DataFrame(job_data)
        df.drop_duplicates(inplace=True)

        os.makedirs("data", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"data/scraped_data_{timestamp}.csv"
        df.to_csv(file_name, index=False)

        print(f"✅ Scraping completed! Data saved to {file_name}")
        logging.info("Scraping completed successfully.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        print(f"❌ Request error: {e}")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    scrape_jobs()
import schedule
import time

# Schedule the scraper
schedule.every().day.at("09:00").do(scrape_jobs)

print("Scheduler is running. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)

if __name__ == "__main__":
    # Run once immediately
    scrape_jobs()

    # Set up scheduler to run daily
    import schedule
    import time

    schedule.every().day.at("09:00").do(scrape_jobs)

    print("⏳ Scheduler is running. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)
