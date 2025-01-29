import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

def scrape_website_from_url(url):
    if url.startswith("www"):
        url = "https://" + url
    try:
        # Set up a headless Firefox browser
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        driver = webdriver.Firefox(options=firefox_options)

        # Load the web page
        driver.get(url)
        print("Launched browser in headless mode to open URL")
        driver.maximize_window()

        # Wait until the page is fully loaded
        timer = 0
        message = False
        while not (message) and timer < 10:
            message = driver.execute_script(
                """
                document.addEventListener("DOMContentLoaded", function(e) {
                console.log("page has loaded");
                return "page has loaded";  // Return message
                });
                return document.readyState === 'complete'; // Check initial readyState
            """
            )

            time.sleep(1)
            timer += 1

        page_source = driver.page_source
        driver.quit()
        print("Browser was closed successfully")

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")

        # Extract the HTML content (only body)
        html_content = soup.find("body").prettify()

        print("HTML Extracted Successfully!")
        return html_content

    except Exception as e:
        # Handle exceptions and print an error message
        print(f"An error occurred: {str(e)}")
        return None