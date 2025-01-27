# Developed by Taylor Jolin for free and open use. 
# Please use responsibly!

import os
import time
import logging
import readline
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import base64
from urllib.parse import urljoin
import platform

# Function to clear the terminal screen for better user experience
def clear_screen():
    # Uses different clear commands depending on the operating system
    if platform.system() == 'Windows':
        os.system('cls')
    else:  # For Linux and macOS
        os.system('clear')

# Clear the terminal screen when starting the program
clear_screen()

# Set up logging to track the program's progress and any errors
# This will show timestamps and log levels (INFO, ERROR, etc.)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Enable file/directory auto-completion when users type paths
# This makes it easier to specify output directories
def complete_path(text, state):
    if text == "":
        text = "."
    if "~" in text:  # Expand ~ to user's home directory
        text = os.path.expanduser(text)
    
    # Split the path into directory and file parts
    dirname = os.path.dirname(text) or "."
    basename = os.path.basename(text)
    
    if os.path.isdir(dirname):
        try:
            # Build a list of possible completions
            completions = []
            for item in os.listdir(dirname):
                if item.startswith(basename):
                    full_path = os.path.join(dirname, item)
                    # Add a trailing slash for directories
                    if os.path.isdir(full_path):
                        completions.append(full_path + "/")
                    else:
                        completions.append(full_path)
            
            # Return one completion at a time
            if state < len(completions):
                return completions[state]
        except Exception:
            pass
    
    return None

# Set up the tab completion feature differently based on operating system
# macOS requires different readline configuration than Linux
if platform.system() == 'Darwin':  # macOS
    import readline
    readline.parse_and_bind("bind ^I rl_complete")
else:  # Linux and others
    import readline
    readline.parse_and_bind("tab: complete")

# Configure which characters should separate words for completion
readline.set_completer_delims(' \t\n;')
readline.set_completer(complete_path)

# Interactive user input section
# Get the main website URL to crawl
print("Please enter the website URL (e.g., https://www.website.org):")
base_website = input().strip()
if not base_website.endswith('/'):
    base_website += '/'

# Allow user to specify a specific section of the website to crawl
print("\nEnter the specific path to crawl (press Enter if none, e.g., 'tools/' or 'docs/'):")
crawl_path = input().strip()
if crawl_path and not crawl_path.endswith('/'):
    crawl_path += '/'

# Get the CSS selector to find specific links on the page
# This allows targeting specific types of links (e.g., article links, navigation links)
print("\nEnter the CSS selector for the links you want to crawl (e.g., 'a.article-link' or 'div.content a'):")
css_selector = input().strip() or "a"  # Use 'a' to select all links if no specific selector given

# Get the directory where downloaded pages should be saved
print("\nPlease enter the output directory path where files should be saved:")
OUTPUT_DIR = os.path.expanduser(input().strip())  # Convert ~ to full home directory path

# Option to create a separate folder for each website's content
print("\nWould you like to create a new folder for this website? (y/n):")
create_subfolder = input().strip().lower().startswith('y')

if create_subfolder:
    # Create a folder name from the website's domain name
    # Replace http:// and periods with underscores for a valid folder name
    folder_name = base_website.replace('https://', '').replace('http://', '').rstrip('/')
    folder_name = folder_name.split('/')[0].replace('.', '_')
    OUTPUT_DIR = os.path.join(OUTPUT_DIR, folder_name)

# Create the output directory if it doesn't exist
try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logging.info(f"Creating directory: {OUTPUT_DIR}")
except Exception as e:
    logging.error(f"❌ Error creating output directory: {e}")
    exit(1)

# Set up Chrome in headless mode (runs without opening a browser window)
# These options optimize Chrome for web scraping
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def clean_filename(url):
    """
    Convert a URL into a valid filename by:
    1. Removing http:// and https:// prefixes
    2. Taking the last part of the URL path
    3. Removing special characters
    4. Adding .html extension if needed
    """
    # Remove common prefixes
    url = url.replace('https://', '').replace('http://', '')
    # Get the last part of the path
    name = url.rstrip('/').split('/')[-1]
    # Remove special characters
    name = ''.join(c for c in name if c.isalnum() or c in '.-_')
    # Add .html extension if not present
    if not name.endswith('.html'):
        name += '.html'
    return name

def get_links():
    """
    Fetch and extract all links from the specified webpage that match the CSS selector.
    Waits for JavaScript content to load and filters out mailto: links.
    Returns a set of unique links.
    """
    full_url = f"{base_website}{crawl_path}"
    logging.info(f"Fetching links from: {full_url}")
    driver.get(full_url)
    time.sleep(5)  # Wait for JavaScript to load content
    links = set()  # Use a set to avoid duplicates

    try:
        elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
        for el in elements:
            href = el.get_attribute("href")
            if href and not href.startswith('mailto:'):  # Skip mailto: links
                links.add(href)
        logging.info(f"✅ Found {len(links)} unique links!")
    except Exception as e:
        logging.error(f"❌ Error fetching links: {e}")
    
    return links

def scrape_pages(links):
    """
    For each link:
    1. Load the page and wait for content
    2. Extract and embed CSS styles
    3. Download and embed images as base64
    4. Save the complete webpage with all resources embedded
    This allows offline viewing of the saved pages with styles and images intact.
    """
    for url in links:
        try:
            logging.info(f"🔍 Fetching: {url}")
            driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Inject CSS styles into the page content
            script = """
            var styles = '';
            var styleSheets = document.styleSheets;
            for (var i = 0; i < styleSheets.length; i++) {
                var rules = styleSheets[i].cssRules || styleSheets[i].rules;
                if (rules) {
                    for (var j = 0; j < rules.length; j++) {
                        styles += rules[j].cssText + '\\n';
                    }
                }
            }
            return styles;
            """
            css_styles = driver.execute_script(script)
            
            # Get the page content
            content = driver.page_source
            
            # Insert the CSS styles into the head of the document
            if '<head>' in content:
                content = content.replace('<head>', f'<head><style>{css_styles}</style>')
            else:
                content = f'<html><head><style>{css_styles}</style></head>{content}</html>'
            
            # Download and embed images
            soup = BeautifulSoup(content, 'html.parser')
            for img in soup.find_all('img'):
                try:
                    if img.get('src'):
                        # Convert relative URLs to absolute
                        img_url = urljoin(url, img['src'])
                        # Download image and convert to base64
                        img_response = requests.get(img_url)
                        if img_response.status_code == 200:
                            img_type = img_response.headers.get('content-type', 'image/jpeg')
                            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                            img['src'] = f'data:{img_type};base64,{img_base64}'
                except Exception as e:
                    logging.error(f"❌ Error processing image {img.get('src')}: {e}")
            
            # Create a clean filename
            file_name = clean_filename(url)
            file_path = os.path.join(OUTPUT_DIR, file_name)
            
            # Save the modified content
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(str(soup))
                logging.info(f"✅ Saved: {file_path}")
        except Exception as e:
            logging.error(f"❌ Error scraping {url}: {e}")

if __name__ == "__main__":
    try:
        links = get_links()
        if links:
            scrape_pages(links)
        else:
            logging.error("❌ No links found. Exiting...")
    except Exception as e:
        logging.error(f"❌ Error occurred: {e}")
    finally:
        driver.quit()
        logging.info("🚀 Scraping complete!")
