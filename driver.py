import argparse, sys, os, json, urllib3, webbrowser

from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchDriverException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List
from totp import get_mfa

class UPass():
    def __init__(self, log_callback=print):
        self.log = log_callback
        self._load_config()
        # Disable SSL Warnings
        urllib3.disable_warnings()

    def _load_config(self):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/config.json') as config:
            config_data: Dict[str, str] = json.load(config)
            self._sfu_usr_pass: Dict[str, str] = {
                'username': config_data['username'],
                'password': config_data['password'],
                'secret_key': config_data['secret_key']
            }
    
    def request(self, driver):
        self._request_upass(driver)

    def _request_upass(self, driver):
        driver.implicitly_wait(5)
        wait = WebDriverWait(driver, timeout=2)

        # Get to U-Pass BC page
        self.log("Opening U-Pass BC")
        driver.get('https://upassbc.translink.ca')
        dropdown = Select(driver.find_element(by=By.ID, value= "PsiId"))
        dropdown.select_by_visible_text('Simon Fraser University')
        goButton = driver.find_element(by=By.ID, value= "goButton")
        goButton.click()
        assert driver.current_url.startswith("https://cas.sfu.ca/cas/login")

        # Initial SFU login
        self.log("Logging in to SFU...")
        sfu_data: Dict[str, str] = self._sfu_usr_pass
        username = driver.find_element(by=By.ID, value="username")
        username.send_keys(sfu_data['username'])
        password = driver.find_element(by=By.ID, value="password")
        password.send_keys(sfu_data['password'])
        submit = driver.find_element(by=By.NAME, value="submit")
        submit.click()

        # Validate that credentials were correct
        assert len(driver.find_elements(by=By.XPATH, value="//div[contains(@class, 'alert alert-danger')]")) == 0, "Invalid credentials! Please check your config file."

        self.log("Initializing MFA...")
        mfa_successful = False
        while(not mfa_successful):
            iframe = driver.find_element(by=By.ID, value='duo_iframe')
            driver.switch_to.frame(iframe)
            mfa_code = get_mfa(sfu_data['secret_key'])
            code = driver.find_element(by=By.ID, value="code")
            code.send_keys(mfa_code)
            submit_mfa = driver.find_element(by=By.XPATH, value="//button[contains(@class, 'ui primary button')]")
            submit_mfa.click()
            self.log("MFA successful!")
            try:
                wait.until(lambda d: driver.current_url.startswith('https://upassbc.translink.ca'))
                mfa_successful = True
            except TimeoutException:
                self.log("Incorrect MFA, reentering...")

         # Check if U-Pass is behaving erroneously or user is given access privileges
        assert driver.current_url != "https://upassbc.translink.ca/home/noprivilege", "❌ Could not login to U-Pass! Either U-Pass site is not working or SFU has not set you up for U-Pass!"

        assert driver.current_url == 'https://upassbc.translink.ca/fs/'

        
        # Check if eligible to request
        try:
            driver.switch_to.default_content()
            checkbox = driver.find_element(by=By.ID, value= "chk_1")
            # Request eligibility
            self.log("🕒 Requesting U-Pass...")
            checkbox.click()
            request_button = driver.find_element(by=By.ID, value="requestButton")
            if request_button.get_attribute("disabled") != None:
                self.log("❌ Unable to request for U-Pass")
            else:
                request_button.click()
                self.log("🟢 Successfully requested U-Pass!")
        # No checkbox option was found
        except NoSuchElementException:
            self.log("❌ Unable to request for U-Pass at this time. U-Pass cen be requested on the 16th of each month.")

