from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from lxml import html
import pandas as pd


def scrape_website_with_js(url):
    try:
        # Set up a headless Firefox browser
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        driver = webdriver.Firefox(options=firefox_options)

        # Load the web page
        driver.get(url)

        # Wait for JavaScript to execute (you can set a specific time or use explicit waits)
        WebDriverWait(driver, 30).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )

        page_source = driver.page_source

        # Close the browser
        driver.quit()
        print("HTML extrected successfully")

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, "html5lib")

        # Extract the HTML content (only body)
        html_content = soup.find("body").prettify()

        return html_content

    except Exception as e:
        # Handle exceptions and print an error message
        print(f"An error occurred: {str(e)}")
        return None

# TODO : lets comment these out

if __name__ == "__main__":
    # url = input("Enter Url: ")
    bankfab_url = "https://business.bankfab.com/"
    pimco_url = "https://www.pimco.com/gbl/en"
    ticker_tape_url = "https://www.tickertape.in/"

    bankfab_csv = "C:\\Users\\akshay.katiha\\Downloads\\bankfab.csv"
    pimco_csv = "C:\\Users\\akshay.katiha\\Downloads\\pimco_xpath.csv"
    tickettape_csv = "C:\\Users\\akshay.katiha\\Downloads\\ticker_tape.csv"

    page_source = scrape_website_with_js(bankfab_url)
    tree = html.fromstring(page_source)

    # read values from csv files
    xpath_column = pd.read_csv(bankfab_csv)
    xpaths = xpath_column.xpath
    total_xpaths = len(xpaths)

    print("There is no code blocks available for following xpaths given below:")
    count = 0
    for index, xpath in enumerate(xpaths):
        code_block = tree.xpath(xpath)

        if not code_block:
            print(f"{index}. {xpath}")
            count += 1

    print(f"Total xpaths = {total_xpaths}, not worked = {count}")
