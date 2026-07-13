from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
import os

from backend.constants import CHROME_BINARY_LOCATION, CHROME_DRIVER_LOCATION, CHROME_BOOT_ARGUMENTS, CHROME_PROFILE_LOCATION


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


def set_input_field_value(driver: webdriver.Chrome, input_field: WebElement, value: str) -> None:
    tag = input_field.tag_name.lower()

    if tag == "input":
        driver.execute_script("""
            arguments[0].focus();
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, input_field, value)
        return

    if tag == "select":
        select = Select(input_field)

        try:
            # Сначала пытаемся выбрать по отображаемому тексту
            select.select_by_visible_text(str(value))
        except:
            try:
                # Если не получилось — по value
                select.select_by_value(str(value))
            except Exception:
                available = [option.text for option in select.options]
                raise ValueError(
                    f'Не удалось выбрать "{value}". '
                    f'Доступные значения: {available}'
                )

        # Для Select2
        driver.execute_script("""
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, input_field)
        return

    raise NotImplementedError(f"Unsupported element: {tag}")

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


def fill_person_form(driver: webdriver.Chrome,
                     person: dict[str, str],
                     template: dict[str, dict]) -> None:
    switch_to_active_window(driver)

    for field, mapping in template.items():
        web_id = mapping["web_id"]

        if not web_id:
            continue

        value = person.get(field, "")
        if value == "":
            continue

        input_field = find_input_field(driver, web_id)
        set_input_field_value(driver, input_field, value)


def confirm_entry(driver: webdriver.Chrome) -> None:
    switch_to_active_window(driver)
    btn = find_button(driver, "Сохранить")
    btn.click()

def open_form_page(driver: webdriver.Chrome) -> None:
    NEW_ENTRY_URL: str = "https://edu.rosmintrud.ru/reestr/pendingEducatedPerson/create?ReturnUrl=https%3A%2F%2Fedu.rosmintrud.ru%2Freestr%2FpendingEducatedPerson%2Flist"
    driver.get(NEW_ENTRY_URL)
