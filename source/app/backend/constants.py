import os

APP_NAME: str = "TableFlip" # Менять этот параметр только если прям очень хочется, но лучше не надо
APP_DATA_FOLDER: str = f"{os.environ.get("APPDATA", "")}\\{APP_NAME}\\"
PUBLIC_KEY: str = ""

DEFAULT_PERSON_TEMPLATE: dict = {
    # Полное имя обязано назыаться "full_name", иначе разделение полного имени на составляющие не будет работать
    "full_name" :               {"show_in_ui": True,  "column_index": -1, "display_name": "ФИО",                       "web_id": ""},
    "last_name" :               {"show_in_ui": False, "column_index": -1, "display_name": "фамилия",                   "web_id": "LastName"},
    'first_name' :              {"show_in_ui": False, "column_index": -1, "display_name": "Имя",                       "web_id": "FirstName"},
    'middle_name' :             {"show_in_ui": False, "column_index": -1, "display_name": "Отчество",                  "web_id": "MiddleName"},
    'snils' :                   {"show_in_ui": True,  "column_index": -1, "display_name": "СНИЛС",                     "web_id": "SnilsTextBoxId"},
    'position' :                {"show_in_ui": True,  "column_index": -1, "display_name": "Профессия (должность)",     "web_id": "Position"},
    'workplace' :               {"show_in_ui": True,  "column_index": -1, "display_name": "Место работы",              "web_id": "EmployerTitle"},
    'workplace_inn' :           {"show_in_ui": True,  "column_index": -1, "display_name": "ИНН работодателя",          "web_id": "EmployerInn"},
    'training_program' :        {"show_in_ui": True,  "column_index": -1, "display_name": "Программа обучения",        "web_id": "LearnProgramIds"}, # 'LearnProgramId' 'LearnProgram'
    'training_org' :            {"show_in_ui": True,  "column_index": -1, "display_name": "Обучающая организация",     "web_id": "OrganizationTitle"},
    'training_org_inn' :        {"show_in_ui": True,  "column_index": -1, "display_name": "ИНН обучающей организации", "web_id": "OrganizationTitle"},
    'knowledge_result' :        {"show_in_ui": True,  "column_index": -1, "display_name": "Результат проверки знаний", "web_id": "IsPassed"},
    'knowledge_check_date' :    {"show_in_ui": True,  "column_index": -1, "display_name": "Дата проверки знаний",      "web_id": "TestDate"},
    'protocol_number' :         {"show_in_ui": True,  "column_index": -1, "display_name": "Номер протокола",           "web_id": "ProtocolNumber"},
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