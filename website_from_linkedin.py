import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.parse import unquote
import csv

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")  # Optional: Run in headless mode
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_website(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Extract company website
    website_tag = soup.select_one("[data-tracking-control-name='about_website']")
    company_website = unquote(website_tag["href"]).split("url=")[1].split("&")[0] if website_tag else None

    return company_website

def process_links(csv_file, output_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    if 'Company LinkedIn' not in df.columns:
        print("Error: 'Company LinkedIn' column not found in the CSV file.")
        return

    # Open the output file in append mode
    with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["Job Title", "Job Post Date", "Job URL", "Job Location", "Company Name", "Company Website", "Company LinkedIn"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, row in df.iterrows():
            linkedin_url = row['Company LinkedIn']
            company_name = row['Company Name']

            if pd.isna(linkedin_url):
                print(f"Skipping empty URL at row {index}.")
                continue

            driver = setup_driver()  # Initialize WebDriver for each company

            try:
                print(f"Processing: {linkedin_url}")
                driver.get(linkedin_url)  # Open the URL

                time.sleep(5)  # Wait for the page to load

                # Get the HTML source of the page
                html_source = driver.page_source

                # Extract website from HTML
                company_website = extract_website(html_source)

                # Write the result to the CSV file
                writer.writerow({
                    "Job Title": row['Job Title'],
                    "Job Post Date": row['Job Post Date'],
                    "Job URL": row['Job URL'],
                    "Job Location": row['Job Location'],
                    "Company Name": company_name,
                    "Company Website": company_website,
                    "Company LinkedIn": linkedin_url
                })

            except Exception as e:
                print(f"Error processing {linkedin_url}: {e}")
            finally:
                driver.quit()  # Close the WebDriver after processing each company

if __name__ == "__main__":
    input_csv = "input"  # Replace with your input CSV file name
    output_csv = "ouput_website.csv"  # Replace with your desired output CSV file name

    process_links(input_csv, output_csv)