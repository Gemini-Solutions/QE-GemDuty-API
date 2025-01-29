import shutil
# TODO : send to general_utils
def is_browser_installed(browser_name):
    if browser_name == "chrome":
        return (
            shutil.which("google-chrome") is not None
            or shutil.which("chromium") is not None
            or shutil.which("chrome") is not None
        )
    elif browser_name == "firefox":
        return shutil.which("firefox") is not None
    elif browser_name == "edge":
        return shutil.which("msedge") is not None
    elif browser_name == "safari":
        return shutil.which("safari") is not None
    return False

# TODO : are the below calls necessary for every run ? 
# Example usage:
browsers = ["chrome", "firefox", "edge", "safari"]
installed_browsers = [browser for browser in browsers if is_browser_installed(browser)]

print(f"Installed browsers: {installed_browsers}")


# def open_url(url):
#     html_doc = None

#     # Use Selenium to load the page with JavaScript execution
#     firefox_options = Options()
#     firefox_options.add_argument("--headless")
#     service = FirefoxService(GeckoDriverManager().install())

#     driver = webdriver.Firefox(service=service, options=firefox_options)

#     driver.get(url)
#     driver.maximize_window()

#     # Wait until the page is fully loaded
#     WebDriverWait(driver, 60).until(
#         lambda d: d.execute_script("return document.readyState") == "complete"
#     )

#     html_doc = driver.page_source
#     driver.quit()
#     print("HTML extracted successfully")
#     return html_doc
