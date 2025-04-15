import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_jobs():
    url = "https://vacancymail.co.zw/jobs/"
    base_url = "https://vacancymail.co.zw"
    jobs = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        job_boxes = soup.find_all("div", class_="job-box")[:10]

        for job in job_boxes:
            try:
                title_tag = job.find("a")
                title = title_tag.text.strip()
                detail_url = base_url + title_tag["href"]

                company = job.find("div", class_="company").text.strip()
                location = job.find("div", class_="location").text.strip()
                expiry = job.find("div", class_="expiry").text.strip()

                # Get job description from the detail page
                detail_resp = requests.get(detail_url)
                detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                desc_tag = detail_soup.find("div", class_="job-description")
                description = desc_tag.text.strip() if desc_tag else "N/A"

                jobs.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Expiry Date": expiry,
                    "Description": description
                })

            except Exception as e:
                logging.warning(f"Error processing a job post: {e}")
                continue

        # Save to CSV
        df = pd.DataFrame(jobs)
        df.drop_duplicates(inplace=True)
        df.to_csv("scraped_data.csv", index=False)

        logging.info("Scraping successful. Data saved to scraped_data.csv")
        print("✅ Scraping complete. Data saved to scraped_data.csv")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch jobs page: {e}")
        print("❌ Failed to fetch job listings. Check your internet or the website.")
    except Exception as e:
        logging.error(f"General error: {e}")
        print("❌ An error occurred. Check scraper.log for details.")

# Only run when this script is executed directly
if __name__ == "__main__":
    scrape_jobs()


