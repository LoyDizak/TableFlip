from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import logging
import time
import os
from typing import Optional

from Parser import Person


fields_mapping = {
    'last_name': ['LastName'],
    'first_name': ['FirstName'],
    'middle_name': ['MiddleName'],
    'snils': ['SnilsTextBoxId', 'Snils'],
    'position': ['Position'],
    'workplace': ['EmployerTitle'],
    'workplace_inn': ['EmployerInn'],
    'training_program': ['LearnProgramIds', 'LearnProgramId', 'LearnProgram'],
    'training_org': ['OrganizationTitle'],
    # NOTE: HTML uses the same name/id for organization title and its INN in this local copy;
    # include both candidates so the function can find the available element.
    'training_org_inn': ['OrganizationTitle', 'OrganizationInn'],
    'knowledge_result': ['IsPassed'],
    'knowledge_check_date': ['TestDate', 'DateTest'],
    'protocol_number': ['ProtocolNumber']
    }


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


def find_info_field_by_name(driver: webdriver.Chrome, candidates: list[str]) -> Optional[WebElement]:
    """
    Ищет HTML элемент на странице по списку возможных идентификаторов.
    
    Пытается найти элемент сначала по ID, затем по NAME для каждого кандидата
    из предоставленного списка.
    
    Параметры:
    - driver: selenium webdriver объект
    - candidates: список возможных ID/NAME элемента
    
    Возвращает:
    - Найденный элемент WebElement или None если элемент не найден
    """
    logging.debug(f"Поиск элемента среди кандидатов: {candidates}")
    for name in candidates:
        try:
            element = driver.find_element(By.ID, name)
            logging.info(f"✓ Элемент найден по ID: {name}")
            return element
        except Exception as e:
            logging.debug(f"  ✗ ID '{name}' не найден")
            pass
        try:
            element = driver.find_element(By.NAME, name)
            logging.info(f"✓ Элемент найден по NAME: {name}")
            return element
        except Exception as e:
            logging.debug(f"  ✗ NAME '{name}' не найден")
            pass
    logging.warning(f"⚠ Ни один из кандидатов не найден: {candidates}")
    return


def set_value(driver: webdriver.Chrome, element: WebElement, value) -> None:
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
        tag_name = element.tag_name.lower()
        logging.debug(f"Установка значения '{value}' для элемента типа '{tag_name}'")
        
        # Handle select elements
        if tag_name == 'select':
            logging.debug(f"Обнаружен SELECT элемент, попытка выбрать опцию")
            # For select, we need to find and click the option with matching value
            try:
                from selenium.webdriver.support.ui import Select
                select = Select(element)
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
                driver.execute_script("arguments[0].focus(); arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));", element, value)
                logging.info(f"✓ Значение установлено через JavaScript для {tag_name}: {value}")
            except Exception as js_error:
                logging.error(f"✗ Ошибка при выполнении JavaScript: {js_error}")
                raise
    except Exception as e:
        logging.debug(f"Попытка использования Selenium API для заполнения")
        try:
            element.clear()
            element.send_keys(value)
            logging.info(f"✓ Значение установлено через Selenium API: {value}")
        except Exception as api_error:
            logging.error(f"✗ Не удалось установить значение через Selenium API: {api_error}")


def open_page(url: str, wait_time: float = 3, use_profile: bool = True) -> Optional[webdriver.Chrome]:
    logging.info(f"═══ Открытие страницы ═══")
    logging.info(f"URL: {url}")
    logging.info(f"Использование сохраненного профиля: {'Да' if use_profile else 'Нет'}")
    
    if url == "" or url.isspace():
        logging.error("✗ Недействительная ссылка")
        return

    try:
        chrome_options = Options()
        chrome_options.binary_location = "chrome-win64/chrome.exe"

        # Сохранение профиля браузера с куками и данными входа
        if use_profile:
            profile_dir = os.path.abspath("./chrome_profile")
            if not os.path.exists(profile_dir):
                os.makedirs(profile_dir)
                logging.info(f"✓ Создана папка профиля: {profile_dir}")
            else:
                logging.info(f"✓ Используется существующий профиль: {profile_dir}")
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")

        # Оптимизирующие флаги для производительности
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-sync")
        # chrome_options.add_argument("--disable-web-resources")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-preconnect")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-breakpad")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-ota-tag-stripping")
        chrome_options.add_argument("--disable-save-password-bubble")
        chrome_options.add_argument("--disable-background-timer-throttling")
        # chrome_options.add_argument("--start-maximized")
        
        # Отключаем изображения для ускорения загрузки
        prefs = {
            "profile.managed_default_content_settings.images": 2  # 2 = отключить изображения
        }
        chrome_options.add_experimental_option("prefs", prefs)

        service = Service(executable_path="chromedriver-win64/chromedriver.exe")

        # Создаем объект браузера
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info(f"✓ ChromeDriver инициализирован с оптимизацией производительности")
        
        # Переходим по URL
        driver.get(url)
        logging.info(f"✓ Переход по URL выполнен")
        logging.info(f"Текущая страница: {driver.current_url}")
        
        # Ждем загрузки страницы
        time.sleep(wait_time)
        
        # Проверяем открытые вкладки
        for i, handle in enumerate(driver.window_handles):
            driver.switch_to.window(handle)
        
        # Если открыто больше одной вкладки, переходим на последнюю
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)  # Даем время на загрузку новой вкладки
        else:
            # Переключаемся на первую (и единственную) вкладку
            driver.switch_to.window(driver.window_handles[0])
        
        # Логируем информацию о странице для отладки
        try:
            page_title = driver.title
        except:
            pass
        
        return driver  # Возвращаем объект driver для дальнейших действий
    except Exception as e:
        return None


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
        info_field = find_info_field_by_name(driver, fields_mapping.get(key, []))
        if info_field:
            set_value(driver, info_field, value)
            filled_count += 1
            time.sleep(wait)
        else:
            logging.warning(f"⚠ Элемент для '{key}' не найден (искали: {fields_mapping.get(key)})")

    # Прочие поля
    other_attrs = ['snils','position','workplace','workplace_inn','training_program','training_org','training_org_inn','knowledge_result','knowledge_check_date','protocol_number']
    for attr in other_attrs:
        val = getattr(person, attr, None)
        if not val:
            logging.debug(f"Поле '{attr}': пусто, пропуск")
            continue
        logging.debug(f"Заполнение '{attr}' = '{val}'")
        info_field = find_info_field_by_name(driver, fields_mapping.get(attr, []))
        if info_field:
            set_value(driver, info_field, val)
            filled_count += 1
            time.sleep(wait)
            continue

        # Попробуем поиск по имени атрибута (name)
        try:
            info_field_name = driver.find_element(By.NAME, attr)
            logging.info(f"✓ Элемент найден по NAME атрибуту: {attr}")
            set_value(driver, info_field_name, val)
            filled_count += 1
            time.sleep(wait)
            continue
        except Exception:
            logging.debug(f"  ✗ NAME атрибут '{attr}' не найден")
            pass

        logging.warning(f"⚠ Поле для '{attr}' не найдено на странице")
    
    logging.info(f"✓ Заполнено полей: {filled_count}")