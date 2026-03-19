from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
import os

from backend.data import Person, PERSON_FIELDS_WEB_MAP, CHROME_BINARY_LOCATION, CHROME_DRIVER_LOCATION, CHROME_BOOT_ARGUMENTS, CHROME_PROFILE_LOCATION


def switch_to_active_window(driver: webdriver.Chrome) -> None:
    all_handles = driver.window_handles
    if len(all_handles) > 1:
        # Переключаемся на последнюю вкладку (обычно активную)
        driver.switch_to.window(all_handles[-1])
    else:
        driver.switch_to.window(all_handles[0])
   

def find_input_field(driver: webdriver.Chrome, field_id: str) -> WebElement:
    try:
        return driver.find_element(By.ID, field_id)
    except:
        print(f"Не послучилось найти кнопку \"{field_id}\"")
        raise


def find_button(driver: webdriver.Chrome, button_value: str) -> WebElement:
    try:
        return driver.find_element(By.XPATH, f"//input[@value='{button_value}']")
    except:
        raise

def set_input_field_value(driver: webdriver.Chrome, input_field: WebElement, value) -> None:
    if input_field.tag_name == 'input': # text field
        driver.execute_script("arguments[0].focus(); arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));", input_field, value)            
    
    if input_field.tag_name == 'select':    
        select = Select(input_field)
        # Try to select by value first
        try:
            select.select_by_value(str(value))
        except:
            print(f"Could not find value \"{value}\" in select options of {input_field.tag_name}")


def open_browser() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY_LOCATION

    for argument in CHROME_BOOT_ARGUMENTS:
        chrome_options.add_argument(argument)

    profile_dir = os.path.abspath(CHROME_PROFILE_LOCATION)
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)

    chrome_options.add_argument(f"--user-data-dir={profile_dir}")

    service = Service(executable_path=CHROME_DRIVER_LOCATION)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def fill_person_form(driver: webdriver.Chrome, person: Person) -> None:
    switch_to_active_window(driver)
    for field_name, field_id in PERSON_FIELDS_WEB_MAP.items():
        input_field: WebElement = find_input_field(driver, field_id)
        input_value: str = getattr(person, field_name)
        set_input_field_value(driver, input_field, input_value)


def fill_person_form_new(driver: webdriver.Chrome, person: dict[str, str], template: dict[str, dict]) -> None:
    switch_to_active_window(driver)
    for field, mapping in template.items():
        if mapping["web_id"] == "":
            continue
        
        input_field: WebElement = find_input_field(driver, mapping["web_id"])
        input_value: str = person[field]
        set_input_field_value(driver, input_field, input_value)


def confirm_entry(driver: webdriver.Chrome) -> None:
    switch_to_active_window(driver)
    btn = find_button(driver, "Сохранить")
    btn.click()
