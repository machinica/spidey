## Spidey

### Overview
This project is a web crawler developed by Taylor Jolin, designed to extract and save web pages from a specified website. It uses Selenium and BeautifulSoup to navigate and scrape content while ensuring that the downloaded pages maintain their styling and images for offline viewing. The tool allows users to specify the website URL, target sub-paths, and CSS selectors to refine the crawling process.

### Features
- Automated Web Crawling: Extracts links from a specified webpage.
- Headless Chrome Scraping: Uses a headless Chrome browser to fetch pages.
- CSS and Image Embedding: Ensures that scraped pages retain their original styling and images.
- Flexible Input Options: Users can specify the website, sub-path, CSS selector, and output directory.
- Automatic Filename Cleaning: Converts URLs into valid filenames for saving.
- Logging for Debugging: Provides real-time logs for tracking progress and errors.

### Installation
Before running the web crawler, install the required dependencies:

``pip install -r requirements.txt``

## Usage

Run the web crawler using:

``python3 spidey.py``

## Enter the requested details interactively:

- Website URL: The base URL of the website to crawl (e.g., https://www.example.com).
- Path to Crawl: Optional sub-directory to focus on (e.g., docs/).
- CSS Selector: Defines which links to extract (e.g., a.article-link).
- Output Directory: Where the scraped pages will be saved.
- Subfolder Creation: Optionally create a new folder named after the website domain.

## How It Works

- Clears the Terminal - Provides a clean UI when starting the script.
- Configures Readline Autocompletion - Enables file path autocompletion for input fields.
- Gathers User Input - Collects URL, path, selector, and output directory from the user.
- Sets Up Chrome WebDriver - Initializes Chrome in headless mode for efficient scraping.
- Extracts Links from the Target Page - Uses Selenium to find links matching the CSS selector.
    -  Scrapes and Saves Webpages
    -  Fetches each page
    -  Extracts and embeds CSS styles
    -  Downloads and embeds images as base64
    -  Saves the page as an offline HTML file
    -  Logs Progress and Errors - Displays messages for each step, including errors encountered.
    -  Closes the Browser - Ensures the WebDriver is terminated properly after execution.

## Requirements
- Python 3.x
- Google Chrome installed

Install dependencies using:

``pip install -r requirements.txt``

## Dependencies
- selenium
- webdriver-manager
- beautifulsoup4
- requests
- logging

## Example Output

After execution, the output directory will contain:

- /output_directory/
- example_com/
- page1.html
- page2.html

Each HTML file retains the original page's styling and images, making it fully viewable offline.

## Notes
If the Chrome browser is not installed or outdated, webdriver-manager will handle the correct driver installation.
The script waits for JavaScript-rendered content before extracting links.

Errors encountered while fetching links or downloading pages will be logged.

## License
This project is open for free use and modification by anyone.

