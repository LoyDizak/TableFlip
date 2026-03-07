from dataclasses import dataclass
import os

@dataclass
class Person:
    full_name: str                          # ФИО
    last_name: str                          # Фамилия
    first_name: str                         # Имя
    middle_name: str                        # Отчество
    snils: str                              # СНИЛС
    position: str                           # Профессия (должность)
    workplace: str                          # Место работы
    workplace_inn: str                      # ИНН организации работодателя
    training_program: str                   # Программа обучения
    training_org: str                       # Организация, проводившая обучение
    training_org_inn: str                   # ИНН организации, проводившей обучение
    knowledge_result: str                   # Результат проверки знаний
    knowledge_check_date: str               # Дата проверки знаний
    protocol_number: str                    # Номер протокола проверки знания

# Расположение необходимых столбцов с информацией. -1 если отсутсвует
@dataclass
class TableLayout:
    full_name: int = -1                          # ФИО
    snils: int = -1                              # СНИЛС
    position: int = -1                           # Профессия (должность)
    workplace: int = -1                          # Место работы
    workplace_inn: int = -1                      # ИНН организации работодателя
    training_program: int = -1                   # Программа обучения
    training_org: int = -1                       # Организация, проводившая обучение
    training_org_inn: int = -1                   # ИНН организации, проводившей обучение
    knowledge_result: int = -1                   # Результат проверки знаний
    knowledge_check_date: int = -1               # Дата проверки знаний
    protocol_number: int = -1                    # Номер протокола проверки знания

APP_NAME: str = "TableFlip" # Менять этот параметр только если прям очень хочется, но лучше не надо
APP_DATA_FOLDER: str = f"{os.environ.get("APPDATA", "")}\\{APP_NAME}\\"
PUBLIC_KEY: str = ""

# Соотнесение навзаний полей класса Person и их русских названий
PERSON_FIELDS_RUSSIAN_NAMES: dict = {
    "full_name": "ФИО",
    "last_name": "Фамилия",
    "first_name": "Имя",
    "middle_name": "Отчество",
    "snils": "СНИЛС",
    "position": "Профессия (должность)",
    "workplace": "Место работы",
    "workplace_inn": "ИНН работодателя",
    "training_program": "Программа обучения",
    "training_org": "Организация обучения",
    "training_org_inn": "ИНН организации обучения",
    "knowledge_result": "Результат проверки знаний",
    "knowledge_check_date": "Дата проверки знаний",
    "protocol_number": "Номер протокола",
}

# Соотнесение навзаний полей класса Person и id полей ввода на сайте
PERSON_FIELDS_WEB_MAP: dict = {
    'last_name': 'LastName',
    'first_name': 'FirstName',
    'middle_name': 'MiddleName',
    'snils': 'SnilsTextBoxId',
    'position': 'Position',
    'workplace': 'EmployerTitle',
    'workplace_inn': 'EmployerInn',
    'training_program': 'LearnProgramIds', # 'LearnProgramId' 'LearnProgram'
    'training_org': 'OrganizationTitle',
    'training_org_inn': 'OrganizationTitle',
    'knowledge_result': 'IsPassed',
    'knowledge_check_date': 'TestDate',
    'protocol_number': 'ProtocolNumber',
}


DEFAULT_PERSON_TEMPLATE: dict = {
    "full_name" :               {"table_index": -1, "value": "", "name": "ФИО",                       "web_id": ""},
    "second_name" :             {"table_index": -1, "value": "", "name": "фамилия",                   "web_id": "LastName"},
    'first_name' :              {"table_index": -1, "value": "", "name": "Имя",                       "web_id": "FirstName"},
    'middle_name' :             {"table_index": -1, "value": "", "name": "Отчество",                  "web_id": "MiddleName"},
    'snils' :                   {"table_index": -1, "value": "", "name": "СНИЛС",                     "web_id": "SnilsTextBoxId"},
    'position' :                {"table_index": -1, "value": "", "name": "Профессия (должность)",     "web_id": "Position"},
    'workplace' :               {"table_index": -1, "value": "", "name": "Место работы",              "web_id": "EmployerTitle"},
    'workplace_inn' :           {"table_index": -1, "value": "", "name": "ИНН работодателя",          "web_id": "EmployerInn"},
    'training_program' :        {"table_index": -1, "value": "", "name": "Программа обучения",        "web_id": "LearnProgramIds"}, # 'LearnProgramId' 'LearnProgram'
    'training_org' :            {"table_index": -1, "value": "", "name": "Организация обучения",      "web_id": "OrganizationTitle"},
    'training_org_inn' :        {"table_index": -1, "value": "", "name": "ИНН организации обучения",  "web_id": "OrganizationTitle"},
    'knowledge_check_result' :  {"table_index": -1, "value": "", "name": "Результат проверки знаний", "web_id": "IsPassed"},
    'knowledge_check_date' :    {"table_index": -1, "value": "", "name": "Дата проверки знаний",      "web_id": "TestDate"},
    'protocol_number' :         {"table_index": -1, "value": "", "name": "Номер протокола",           "web_id": "ProtocolNumber"},
}


CHROME_BINARY_LOCATION: str = "chrome\\chrome-win64\\chrome.exe"
CHROME_DRIVER_LOCATION: str = "chrome\\chromedriver-win64\\chromedriver.exe"
CHROME_PROFILE_LOCATION: str = APP_DATA_FOLDER + "chrome profile"
CHROME_BOOT_ARGUMENTS: list[str] = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-sync",
    # "--disable-web-resources",
    "--disable-default-apps",
    "--disable-preconnect",
    "--disable-background-networking",
    "--disable-breakpad",
    "--disable-hang-monitor",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-client-side-phishing-detection",
    "--disable-ota-tag-stripping",
    "--disable-save-password-bubble",
    "--disable-background-timer-throttling",
]