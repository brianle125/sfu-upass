import os
import json
import urllib3
import requests
import webbrowser

from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from lxml import html, etree
from typing import Dict, List

class UPass():
    def __init__(self):
        self._load_config()
        # Disable SSL Warnings
        urllib3.disable_warnings()

    def _load_config(self):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/config.json') as config:
            config_data: Dict[str, str] = json.load(config)
            self._sfu_usr_pass: Dict[str, str] = {
                'username': config_data['username'],
                'password': config_data['password']
            }
            # IFTTT is optional config
            self._ifttt: Dict[str, str] = {
                'event_name': config_data.get('ifttt_event', ''),
                'key': config_data.get('ifttt_key', '')
            }
    
    def request(self):
        self._request_upass()

    def upass(self):
        # Suppress info msg: 'Created TensorFlow Lite XNNPACK delegate for CPU.'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--log-level=2')
        driver = webdriver.Chrome(options=chrome_options)

        # Get to Upassbc page
        driver.get('https://upassbc.translink.ca')
        dropdown = Select(driver.find_element(by=By.ID, value= "PsiId"))
        dropdown.select_by_visible_text('Simon Fraser University')
        goButton = driver.find_element(by=By.ID, value= "goButton")
        goButton.click()
        assert driver.current_url.startswith("https://cas.sfu.ca/cas/login")

        # Initial SFU login
        sfu_data: Dict[str, str] = self._sfu_usr_pass
        username = driver.find_element(by=By.ID, value="username")
        username.send_keys(sfu_data['username'])
        password = driver.find_element(by=By.ID, value="password")
        password.send_keys(sfu_data['password'])
        submit = driver.find_element(by=By.NAME, value="submit")
        submit.click()

        # SFU MFA
        iframe = driver.find_element(by=By.ID, value='duo_iframe')
        driver.switch_to.frame(iframe)
        mfa_code = input("Enter your MFA code: ")
        code = driver.find_element(by=By.ID, value="code")
        code.send_keys(mfa_code)

        # To-do: check for invalid MFA input
        submit_mfa = driver.find_element(by=By.XPATH, value="//button[contains(@class, 'ui primary button')]")
        submit_mfa.click()

        # To do: have a better way of waiting for the UPass page to load
        sleep(5)

        # Check if eligible to request
        assert driver.current_url == 'https://upassbc.translink.ca/fs/'
        checkbox_elems = driver.find_elements(by=By.XPATH, value="//input[@type='checkbox']")

        if len(checkbox_elems) == 0:
            print("Unable to request for UPass at this time.")
        else:
            # Request eligibility
            for checkbox in checkbox_elems:
                checkbox.click()
            
            request_button = driver.find_element(by=By.ID, value="requestButton")
            if request_button.get_attribute("disabled") == "disabled":
                print("Unable to request for UPass")
            else:
                request_button.click()
                print("Successfully requested UPass!")


if __name__ == '__main__':
    upass = UPass()
    upass.upass()
