import os
import re
import json
import time
import validators
import hashlib
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from collections import OrderedDict
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from logger import logger
from utils.login import login_mymis, login_gembook, login_athena


def create_filename_from_hash(url):
    """This method converts the DOM structure into a hash used to name xpath file."""
    return hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'


def create_filename_from_url(url):
    """This method creates a human readable name from the given URL."""
    file_name = re.sub(r"^https?://(www\.)?", "", url)
    file_name = re.sub(r"\.(com|in|io|org|net|gov|edu|uk|co\.\w+)(/|$)", "", file_name)
    file_name = re.sub(r'[\/\?%*:|"<>=]|&.*', "", file_name)
    return file_name + ".json"


def open_url(url, action):
    """This method launch the given URL in headless mode to fetch page object."""
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)

    try:
        html_doc = None

        # Login of internal application will happen here
        if "No-Login" in action:
            if "mis" in url:
                login_mymis(driver)
            elif "gembook" in url:
                login_gembook(driver)
            elif "athena" in url:
                login_athena(driver)
            time.sleep(2)
            logger.info("Application was logged in successfully")
            print("Application was logged in successfully")

        # Now open the URL that user has given to redirect
        if url.endswith("/"):
            url = url[:-1]
        driver.get(url)
        driver.maximize_window()

        # Wait until the page is fully loaded
        timer = 0
        message = False
        while not(message) and timer < 10:
            message = driver.execute_script("""
                document.addEventListener("DOMContentLoaded", function(e) {
                console.log("page has loaded");
                return "page has loaded";  // Return message
                });
                return document.readyState === 'complete'; // Check initial readyState
            """)

            time.sleep(2)
            timer += 1

        html_doc = driver.page_source
        logger.info("Source code extracted successfully")
        print("Source code extracted successfully")
        return html_doc
    except RuntimeError as e:
        logger.info(
            f"Exception {e} occurred when opening browser to extract DOM structure"
        )
        print(f"Exception {e} occurred when opening browser to extract DOM structure")
        raise e
    finally:
        driver.quit()


def create_xpaths_from_page_source(html_doc):
    """This method identifies elements required for the xpath."""
    soup = BeautifulSoup(html_doc, "html.parser")

    # List of tags to parse
    tags = [
        "a",
        "button",
        "div",
        "i",
        "iframe",
        "input",
        "label",
        "header",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "select",
        "span",
        "svg",
        "textarea",
    ]

    high_priority_tags = [
        "a",
        "button",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "input",
        "textarea",
        "td",
        "th",
    ]

    # Create an ordered dictionary to store xpaths
    xpath_dictionary = OrderedDict()
    duplicate_xpath_counter = OrderedDict()

    def manage_duplicate_xpath_name(xpath_name, xpath_value):
        if xpath_name in duplicate_xpath_counter:
            # If xpath name exists, append 1 at the end of previous locator created and delete the old key
            new_xpath_name = (
                xpath_name + "_" + str(duplicate_xpath_counter[xpath_name] + 1)
            )
            xpath_dictionary[new_xpath_name] = xpath_value
            duplicate_xpath_counter[xpath_name] += 1

        else:
            xpath_dictionary[xpath_name] = xpath_value
            duplicate_xpath_counter[xpath_name] = 1

    # Creating xpaths for svg and ion-icon tags seperately
    # Support for feather icon is completely available, for others, the xpaths are created but not named
    svg_elements = soup.find_all("svg")
    for element in svg_elements:
        if element.name == "svg":
            # checking for class attribute only for now
            class_attr_value = element.get("class")
            if class_attr_value:
                if isinstance(class_attr_value, list):
                    class_attr_value = " ".join(class_attr_value)
                if "feather " in class_attr_value:
                    attribute_value = class_attr_value.split(" ")[1]
                    xpath_name = attribute_value.replace("-", "_") + "_icon"
                    xpath_value = (
                        f"//*[local-name()='svg' and contains(@class,'{attribute_value}')]"
                    )
                    manage_duplicate_xpath_name()

    ionicon_elements = soup.find_all("ion-icon")
    for element in ionicon_elements:
        possible_attributes = ["name", "ios", "md", "aria-label", "class"]
        for attribute in possible_attributes:
            attr_value = element.get(attribute)
            if attr_value:
                xpath_name = attr_value.replace("-", "_") + "_icon"
                xpath_value = f"//ion-icon[@{attribute} = {attr_value}]"
                manage_duplicate_xpath_name()

    for index, tag in enumerate(tags, 1):
        all_elements = soup.find_all(tag)

        for element in all_elements:
            # Create xpaths for high-priority tags
            if tag in high_priority_tags:
                xpath_value = select_xpath_attribute(element)
                if xpath_value:
                    if isinstance(xpath_value, tuple):
                        manage_duplicate_xpath_name(xpath_value[0], xpath_value[1])
                    else:
                        xpath_name = generate_xpath_name(element, index)

                        if "delete_this_element_37" in xpath_name:
                            child_xpath_name = find_key_in_children(element)

                            if child_xpath_name is not None:
                                xpath_name = child_xpath_name

                        manage_duplicate_xpath_name(xpath_name, xpath_value)

            else:
                ancestors = [ancestor.name for ancestor in element.find_parents()]

                if (
                    not any(parent in ancestors for parent in high_priority_tags)
                    and not element.find()
                ):
                    xpath_value = select_xpath_attribute(element)
                    if xpath_value:
                        if isinstance(xpath_value, tuple):
                            manage_duplicate_xpath_name(xpath_value[0], xpath_value[1])
                        else:
                            xpath_name = generate_xpath_name(element, index)
                            manage_duplicate_xpath_name(xpath_name, xpath_value)

    return xpath_dictionary


def find_key_in_children(element):
    """Recursively searches for a naming attribute in child elements."""
    if element.name == "a":
        element_name = "_link"
    else:
        element_name = "_" + element.name

    for child in element.descendants:
        if isinstance(child, Tag):  # Ensure it's a tag element
            # Check if any child has a valid naming attribute
            if child.string and str(child.string).strip():
                return snake_case_convertor(child.string) + element_name
            elif child.get("label"):
                return snake_case_convertor(child.get("label")) + element_name
            elif child.get("aria-label"):
                return snake_case_convertor(child.get("aria-label")) + element_name
            elif child.get("placeholder"):
                return snake_case_convertor(child.get("placeholder")) + element_name
            elif child.get("onclick"):
                return snake_case_convertor(child.get("onclick")) + element_name
            elif child.get("formcontrolname"):
                return snake_case_convertor(child.get("formcontrolname")) + element_name
            elif element.get("ng-reflect-text"):
                return snake_case_convertor(element.get("ng-reflect-text"))
            elif element.get("ptooltip"):
                return snake_case_convertor(element.get("ptooltip"))

    # Return None if no naming attribute was found in any descendants
    return None


def get_element_text(element):
    """This method returns the text of the element and not of it's children."""
    complete_text = element.get_text(strip=True)
    child_text = "".join(child.get_text(strip=True) for child in element.find_all())
    element_text = complete_text.replace(child_text, "")

    # Extracted text may contain single quotes, using excape sequences to fix that
    element_text = element_text.replace("'", "\\'")

    # Extracted text may contain characters other than ascii
    element_text = element_text.encode("utf-8").decode("unicode_escape").strip()
    return element_text or None


def select_xpath_attribute(element):
    """Generate XPath for a given element based on its attributes."""
    tag = element.name

    element_text = get_element_text(element)
    if element_text:
        return f"//{tag}[contains(text(), '{element_text}')]"

    attributes = element.attrs
    atributes_to_remove = []
    first_class_attributes = [
        "href",
        "src",
        "placeholder",
        "title",
        "aria-label",
        "label",
        "type",
    ]

    for attribute, value in attributes.items():
        if attribute in first_class_attributes:
            atributes_to_remove.append("attribute")
            return f"//{tag}[@{attribute} = '{value}']"

    for attribute in atributes_to_remove:
        del attributes[attribute]

    possible_icons = [
        "fa fa-",
        "pi pi-",
        "material-icons",
        "bi bi-",
        "fas fa-",
        "ri-",
        "la la-",
        "typcn typcn-",
        "bx bx-",
    ]

    if element.get("class"):
        class_attr_value = element.get("class")
        if isinstance(class_attr_value, list):
            class_attr_value = " ".join(class_attr_value)
        for icon in possible_icons:
            if icon in class_attr_value:
                xpath_name = class_attr_value.split(icon)[1] + "_icon"
                xpath_value = f"//{tag}[@class='{class_attr_value}']"

                return xpath_name, xpath_value

    if element.get("data-feather"):
        attr_value = element.get("data-feather")
        xpath_name = attr_value.replace("-", "_") + "_icon"
        xpath_value = f"//{tag}[@data-feather = {attr_value}]"
        return xpath_name, xpath_value

    if element.get("data-icon"):
        attr_value = element.get("data-icon")
        xpath_name = attr_value.replace("-", "_") + "_icon"
        xpath_value = f"//{tag}[@data-icon = {attr_value}]"
        return xpath_name, xpath_value

    second_class_attributes = ["id", "name", "value", "role"]

    for attribute, value in attributes.items():
        if attribute in second_class_attributes:
            atributes_to_remove.append("attribute")
            return f"//{tag}[@{attribute} = '{value}']"

    for attribute in atributes_to_remove:
        del attributes[attribute]

    third_class_attributes = ["ptooltip", "ng-reflect-text"]
    # For other framework specific attributes
    for attribute in third_class_attributes:
        if element.get(attribute):
            atributes_to_remove.append(attribute)
            return f"//{tag}[@{attribute} = '{element.get(attribute)}']"

    for attribute in atributes_to_remove:
        del attributes[attribute]

    return None


def generate_xpath_name(element, index):
    """This method creates names for the xpaths."""

    key = None
    element_text = get_element_text(element)
    if element_text:
        key = snake_case_convertor(element_text)
    elif element.get("placeholder"):
        key = snake_case_convertor(element.get("placeholder"))
    elif element.get("label"):
        key = snake_case_convertor(element.get("label"))
    elif element.get("aria-label"):
        key = snake_case_convertor(element.get("aria-label"))
    elif element.get("onclick"):
        key = snake_case_convertor(element.get("onclick"))
    elif element.get("formcontrolname"):
        key = snake_case_convertor(element.get("formcontrolname"))
    elif element.get("ng-reflect-text"):
        key = snake_case_convertor(element.get("ng-reflect-text"))
    elif element.get("ptooltip"):
        key = snake_case_convertor(element.get("ptooltip"))

    # Some elements will appear without any name. These elements are named using string
    # 'delete_this_node_37' so that these elements can be identified later and deleted.
    if element.name == "a":
        key = key + "_link" if key else "delete_this_element_37" + str(index)
    elif element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        key = key + "_heading" if key else "delete_this_element_37" + str(index)
    else:
        key = key + "_" + element.name if key else "delete_this_element_37" + str(index)

    return key

def clean_generated_xpaths(xpath_dictionary, user_input):
    """This method filters final keys and values that will be generated to the user."""
    # Create a list of keys to delete
    keys_to_delete = [
        key
        for key in xpath_dictionary.keys()
        if key.startswith("delete_this_element_37")
    ]
 
    # Remove the keys from the dictionary
    for key in keys_to_delete:
        del xpath_dictionary[key]
 
    current_folder = os.path.dirname(os.path.abspath(__file__))
    if validators.url(user_input):
        file_name = create_filename_from_url(user_input)
    else:
        file_name = create_filename_from_hash(user_input)
 
    locator_file = os.path.join(current_folder, file_name)
 
    all_xpaths = [value for value in xpath_dictionary.values() if value]
    unique_xpaths = list(OrderedDict.fromkeys(all_xpaths))
 
    for xpath in unique_xpaths:
        index = 0
        for key, value in xpath_dictionary.items():
            if xpath == value and all_xpaths.count(xpath) > 1:
                index += 1
                xpath_dictionary[key] = f"({xpath})[{index}]"
 
    return xpath_dictionary


def snake_case_convertor(raw_string):
    """This method converts any string to snake case format"""
    if not isinstance(raw_string, str):
        raw_string = str(raw_string)
 
    words = "".join(
        char.lower()
        for char in raw_string.strip()
        if char.isalnum() or char == "_" or char == " "
    )
 
    return words.replace(" ", "_")


def get_raw_xpath_dictionary(url:str,action_type:str)->dict:
    filename = create_filename_from_url(url)
    cache_path = os.path.join('xpath_cache', filename)

    logger.info(f"cache file name : {filename}")

    # Check if cached data exists
    if os.path.exists(cache_path):
        logger.info(f"Loading cached data for {url}")
        try:
            with open(cache_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logger.warning(f"Cache file for {url} is corrupted. Re-fetching data.")
    # If no cache, fetch and save the data
    logger.info(f"Fetching data for {url}")  

    is_url = validators.url(url)

    # validators checks for invalid URL
    if is_url:
        html_doc = open_url(url, action_type)
    else:
        html_doc = url

    data = create_xpaths_from_page_source(html_doc)
    data = clean_generated_xpaths(data, url)
    os.makedirs('xpath_cache', exist_ok=True)  
    with open(cache_path, 'w') as file:
        json.dump(data, file,indent=4)

    return data
