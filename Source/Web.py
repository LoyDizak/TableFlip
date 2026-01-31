from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import logging
import time
import os
from typing import Optional

from data import Person, PERSON_FIELDS_WEB_MAP, CHROME_BINARY_LOCATION, CHROME_DRIVER_LOCATION, CHROME_BOOT_ARGUMENTS, CHROME_PROFILE_LOCATION


def switch_to_active_window(driver: webdriver.Chrome) -> None:
    """
    Переключает драйвер на последнюю открытую (активную) вкладку браузера.
    Это полезно когда пользователь вручную открывает новые вкладки.
    """
    try:
        all_handles = driver.window_handles
        if len(all_handles) > 1:
            # Переключаемся на последнюю вкладку (обычно активную)
            driver.switch_to.window(all_handles[-1])
            logging.info(f"✓ Переключено на последнюю вкладку: {driver.current_url}")
        else:
            driver.switch_to.window(all_handles[0])
            logging.debug(f"Активная вкладка: {driver.current_url}")
    except Exception as e:
        logging.error(f"✗ Ошибка при переключении на активную вкладку: {e}")


def find_input_field(driver: webdriver.Chrome, field_id: str) -> Optional[WebElement]:
    element = driver.find_element(By.ID, field_id)
    return element

    # element = driver.find_element(By.NAME, name)
    # return element


def set_input_field_value(driver: webdriver.Chrome, input_field: WebElement, value) -> None:
    """
    Устанавливает значение HTML элементу на странице.
    
    Поддерживает различные типы элементов (select, input и т.д.).
    Для select элементов использует Select API, для остальных — JavaScript injection.
    
    Параметры:
    - driver: selenium webdriver объект
    - element: WebElement для заполнения
    - value: значение для установки
    """
    try:
        tag_name = input_field.tag_name.lower()
        logging.debug(f"Установка значения '{value}' для элемента типа '{tag_name}'")
        
        # Handle select elements
        if tag_name == 'select':
            logging.debug(f"Обнаружен SELECT элемент, попытка выбрать опцию")
            # For select, we need to find and click the option with matching value
            try:
                from selenium.webdriver.support.ui import Select
                select = Select(input_field)
                # Try to select by value first
                try:
                    select.select_by_value(str(value))
                    logging.info(f"✓ Опция выбрана по значению: {value}")
                except Exception:
                    # If value doesn't match, try by visible text
                    select.select_by_visible_text(str(value))
                    logging.info(f"✓ Опция выбрана по видимому тексту: {value}")
            except Exception as e:
                logging.error(f"✗ Не удалось выбрать опцию в select: {e}")
        else:
            # For text inputs and other fields
            try:
                driver.execute_script("arguments[0].focus(); arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));", input_field, value)
                logging.info(f"✓ Значение установлено через JavaScript для {tag_name}: {value}")
            except Exception as js_error:
                logging.error(f"✗ Ошибка при выполнении JavaScript: {js_error}")
                raise
    except Exception as e:
        logging.debug(f"Попытка использования Selenium API для заполнения")
        try:
            input_field.clear()
            input_field.send_keys(value)
            logging.info(f"✓ Значение установлено через Selenium API: {value}")
        except Exception as api_error:
            logging.error(f"✗ Не удалось установить значение через Selenium API: {api_error}")


def open_page(url: str, use_profile: bool = True) -> Optional[webdriver.Chrome]:
    if url == "" or url.isspace():
        return

    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY_LOCATION

    # Сохранение профиля браузера с куками и данными входа
    if use_profile:
        profile_dir = os.path.abspath(CHROME_PROFILE_LOCATION)
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        else:
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")

    for argument in CHROME_BOOT_ARGUMENTS:
        chrome_options.add_argument(argument)
    
    # Отключаем изображения для ускорения загрузки
    # prefs = {
    #     "profile.managed_default_content_settings.images": 2  # 2 = отключить изображения
    # }
    # chrome_options.add_experimental_option("prefs", prefs)

    service = Service(executable_path=CHROME_DRIVER_LOCATION)

    # Создаем объект браузера
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Переходим по URL
    driver.get(url)

    # Ждем загрузки страницы
    # time.sleep(wait_time)
    
    # Проверяем открытые вкладки
    for i, handle in enumerate(driver.window_handles):
        driver.switch_to.window(handle)
    
    # Если открыто больше одной вкладки, переходим на последнюю
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
        # time.sleep(2)
    else:
        # Переключаемся на первую (и единственную) вкладку
        driver.switch_to.window(driver.window_handles[0])
    
    return driver  # Возвращаем объект driver для дальнейших действий



def diagnose_page(driver: webdriver.Chrome) -> None:
    """
    Выводит диагностическую информацию о странице для отладки
    """
    
    inputs = driver.find_elements(By.TAG_NAME, 'input')
    for i, inp in enumerate(inputs[:20]):  # Первые 20
        inp_id = inp.get_attribute('id')
        inp_name = inp.get_attribute('name')
        inp_type = inp.get_attribute('type')

    selects = driver.find_elements(By.TAG_NAME, 'select')
    for i, sel in enumerate(selects[:20]):  # Первые 20
        sel_id = sel.get_attribute('id')
        sel_name = sel.get_attribute('name')


    textareas = driver.find_elements(By.TAG_NAME, 'textarea')
    for i, ta in enumerate(textareas[:10]):
        ta_id = ta.get_attribute('id')
        ta_name = ta.get_attribute('name')
  


def fill_person_form(driver: webdriver.Chrome, person: Person, wait: float = 0) -> None:
    """
    Заполняет поля страницы данными из объекта `Person`.

    Логика:
    - ВСЕГДА переключается на последнюю активную вкладку перед заполнением
    - Для каждого поля пытается найти элемент по списку возможных id/name.
    - Если элемент найден, устанавливает значение и генерирует событие `change`.
    - Для незнакомых полей — пытается установить по имени поля (атрибут name).

    Параметры:
    - driver: selenium webdriver
    - person: объект `Person` из `Parser.py`
    - wait: пауза между заполнением полей (секунды)
    """
    # ВАЖНО: Переключаемся на активную вкладку перед заполнением
    switch_to_active_window(driver)
    
    logging.info(f"\n═══ Заполнение формы для: {person.full_name if person.full_name else person.last_name} ═══")
    logging.info(f"URL страницы: {driver.current_url}")
    
    # Выводим диагностику если ничего не найдено в предыдущий раз
    diagnose_page(driver)
    
    names = {
        'last_name': person.last_name,
        'first_name': person.first_name,
        'middle_name': person.middle_name
    }

    filled_count = 0
    for key, value in names.items():
        if not value:
            logging.debug(f"Поле '{key}': пусто, пропуск")
            continue
        logging.debug(f"Заполнение '{key}' = '{value}'")
        info_field = find_input_field(driver, PERSON_FIELDS_WEB_MAP.get(key, ""))
        if info_field:
            set_input_field_value(driver, info_field, value)
            filled_count += 1
            time.sleep(wait)
        else:
            logging.warning(f"⚠ Элемент для '{key}' не найден (искали: {PERSON_FIELDS_WEB_MAP.get(key, "")})")

    # Прочие поля
    other_attrs = ['snils','position','workplace','workplace_inn','training_program','training_org','training_org_inn','knowledge_result','knowledge_check_date','protocol_number']
    for attr in other_attrs:
        val = getattr(person, attr, None)
        if not val:
            logging.debug(f"Поле '{attr}': пусто, пропуск")
            continue
        logging.debug(f"Заполнение '{attr}' = '{val}'")
        info_field = find_input_field(driver, PERSON_FIELDS_WEB_MAP.get(attr, ""))
        if info_field:
            set_input_field_value(driver, info_field, val)
            filled_count += 1
            time.sleep(wait)
            continue

        # Попробуем поиск по имени атрибута (name)
        try:
            info_field_name = driver.find_element(By.NAME, attr)
            logging.info(f"✓ Элемент найден по NAME атрибуту: {attr}")
            set_input_field_value(driver, info_field_name, val)
            filled_count += 1
            time.sleep(wait)
            continue
        except Exception:
            logging.debug(f"  ✗ NAME атрибут '{attr}' не найден")
            pass

        logging.warning(f"⚠ Поле для '{attr}' не найдено на странице")
    
    logging.info(f"✓ Заполнено полей: {filled_count}")