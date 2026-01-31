from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
import os

from data import Person, PERSON_FIELDS_WEB_MAP, CHROME_BINARY_LOCATION, CHROME_DRIVER_LOCATION, CHROME_BOOT_ARGUMENTS, CHROME_PROFILE_LOCATION


def switch_to_active_window(driver: webdriver.Chrome) -> None:
    all_handles = driver.window_handles
    if len(all_handles) > 1:
        # Переключаемся на последнюю вкладку (обычно активную)
        driver.switch_to.window(all_handles[-1])
    else:
        driver.switch_to.window(all_handles[0])
   

def get_input_field(driver: webdriver.Chrome, field_id: str) -> WebElement:
    return driver.find_element(By.ID, field_id)

def set_input_field_value(driver: webdriver.Chrome, input_field: WebElement, value) -> None:
    if input_field.tag_name == 'input': # text field
        driver.execute_script("arguments[0].focus(); arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));", input_field, value)            
    
    if input_field.tag_name == 'select':    
        select = Select(input_field)
        # Try to select by value first
        try:
            select.select_by_value(str(value))
        except Exception:
            print(f"Could not find value \"{value}\" in select options of {input_field.tag_name}")


def open_page(url: str) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY_LOCATION

    for argument in CHROME_BOOT_ARGUMENTS:
        chrome_options.add_argument(argument)
    
    # Сохранение профиля браузера с куками и данными входа
    profile_dir = os.path.abspath(CHROME_PROFILE_LOCATION)
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
    else:
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")

    service = Service(executable_path=CHROME_DRIVER_LOCATION)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    
    return driver  # Возвращаем объект driver для дальнейших действий

def fill_person_form(driver: webdriver.Chrome, person: Person) -> None:
    for field_name, field_id in PERSON_FIELDS_WEB_MAP.items():
        set_input_field_value(driver, get_input_field(driver, field_id), getattr(person, field_name))