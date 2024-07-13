import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import os
from datetime import datetime
import csv
import pyttsx3

# Define the list of sitemap URLs
sitemap_urls_list = [
    'https://banglasobis.blogspot.com//sitemap.xml',
    # Add more sitemap URLs here as needed
]

# Function to extract URLs from a given sitemap.xml URL
def extract_urls_from_sitemap(url):
    urls = []
    try:
        # Fetch the sitemap.xml content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'xml')

        # Find all <loc> tags (URLs) within the sitemap
        loc_tags = soup.find_all('loc')
        for loc in loc_tags:
            urls.append(loc.text)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return urls

# Function to save extracted URLs to a CSV file with custom filename
def save_urls_to_csv(urls, domain_name, count_urls):
    current_time = datetime.now()
    filename = f"{domain_name}_{count_urls}_Urls_{current_time.year}_{current_time.month:02d}_{current_time.strftime('%B')}_{current_time.hour:02d}_{current_time.strftime('%M_%p')}.csv"
    file_path = os.path.abspath(filename)
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for url in urls:
                writer.writerow([url])
        print(f"Extracted URLs saved to: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error saving URLs to CSV: {e}")
        return None

# Function to open a file with its associated application (Windows-specific)
def open_file(file_path):
    try:
        if os.name == 'nt':  # Check if running on Windows
            os.startfile(file_path)
        else:
            print("Auto-open not supported on this platform.")
    except Exception as e:
        print(f"Error opening file: {e}")

# Function to speak a notification using text-to-speech
def speak_notification():
    try:
        engine = pyttsx3.init()

        # Adjust speech rate (speed), default is 200
        engine.setProperty('rate', 150)  # Adjust as needed, lower values slow down speech

        engine.say("Hey sharif, Code Running, Finished.")  # Corrected spelling and grammar
        engine.runAndWait()
    except Exception as e:
        print(f"Error speaking notification: {e}")

# Main function to orchestrate the process
def main():
    total_urls = 0

    # Use ThreadPoolExecutor for concurrent processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for sitemap_url in sitemap_urls_list:
            futures.append(executor.submit(extract_urls_from_sitemap, sitemap_url))

        # Use tqdm for progress tracking
        pbar = tqdm(total=len(futures), desc='Extracting URLs')

        # Process each future as it completes
        all_urls = []
        for future in futures:
            try:
                sitemap_urls = future.result()
                if sitemap_urls:
                    all_urls.extend(sitemap_urls)
                    total_urls += len(sitemap_urls)
            except Exception as e:
                print(f"Error extracting URLs: {e}")

            pbar.update(1)

        pbar.close()

    print(f"Total URLs extracted: {total_urls}")

    if total_urls > 0:
        # Extract domain name from one of the URLs (assuming all are from the same domain)
        domain_name = all_urls[0].split('/')[2]

        # Save extracted URLs to CSV file
        file_path = save_urls_to_csv(all_urls, domain_name, total_urls)

        if file_path:
            # Open the file after saving
            open_file(file_path)

            # Speak notification
            speak_notification()
    else:
        print("No URLs extracted. Check your sitemap URLs and network connection.")

if __name__ == "__main__":
    main()
