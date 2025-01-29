from dotenv import dotenv_values
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)


def login_gembook(driver):
    """This method contains code to login Gembook application."""
    try:
        driver.get("https://gembookuibeta.geminisolutions.com")
        driver.maximize_window()

        # Wait for the sign-in button and click it
        sign_in_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'mail')]"))
        )
        sign_in_button.click()

        # Wait for the email field and enter email
        email_field = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type = 'email']"))
        )
        email_field.send_keys(dotenv_values(".env")["GEMBOOK_USERNAME"])

        # Wait for the next button and click it
        next_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value = 'Next']"))
        )
        next_button.click()

        # Wait for the password field and enter password
        password_field = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type = 'password']"))
        )
        password_field.send_keys(dotenv_values(".env")["GEMBOOK_PASSWORD"])

        # Wait for the sign-in button and click it
        sign_in_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value = 'Sign in']"))
        )
        sign_in_button.click()

        # Wait until the 'Directory' element appears after login
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(text(), 'All Posts')]")
            )
        )
    except TimeoutException as e:
        print("Timeout occurred when logging Gembook application")
        raise e
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        raise e
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        raise e
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e


def login_mymis(driver):
    """This method contains code to login MIS application."""
    try:
        driver.get("https://mymis.geminisolutions.com")
        driver.maximize_window()

        # Wait for the username field and enter username
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='username']"))
        )
        username_field = driver.find_element(By.XPATH, "//input[@id='username']")
        username_field.send_keys(dotenv_values(".env")["MIS_USERNAME"])

        # Wait for the password field and enter password
        password_field = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='password']"))
        )
        password_field.send_keys(dotenv_values(".env")["MIS_PASSWORD"])

        # Wait for the sign-in button and click it
        sign_in_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='btnLogin']"))
        )
        sign_in_button.click()

        # Wait until the 'Directory' element appears after login
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(),'Directory')]")
            )
        )
    except TimeoutException as e:
        print("Timeout occurred when logging MIS application")
        raise e
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        raise e
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        raise e
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e


def login_athena(driver):
    """This method contains code to login Athena application."""
    try:
        driver.get("https://dev-athena.geminisolutions.com/login")
        driver.maximize_window()

        # Wait for the username field and enter username
        username_field = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@formcontrolname='username']")
            )
        )
        username_field.send_keys(dotenv_values(".env")["ATHENA_USERNAME"])

        # Wait for the password field and enter password
        password_field = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@formcontrolname='password']")
            )
        )
        password_field.send_keys(dotenv_values(".env")["ATHENA_PASSWORD"])

        # Wait for the sign-in button and click it
        sign_in_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Sign in')]"))
        )
        sign_in_button.click()

        # Wait for user to login successfully
        WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'logo.svg')]"))
        )
    except TimeoutException as e:
        print("Timeout occurred when logging Athena application")
        raise e
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        raise e
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        raise e
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
