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

APP_NAME: str = "DOCX Analyze II" # Менять этот параметр только если прям очень хочется, но лучше не надо
APP_DATA_FOLDER: str = f"{os.environ.get("APPDATA", "")}\\{APP_NAME}\\"
PUBLIC_KEY: str = "" #"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxNWoYNETy4I7W1VoMuOZir7KE6ygbvNajvK+pIxUK7MnvSbwUuXddoah1tPJHpR4gSlaZlg84yKrJOnumRSTDSByyPy7EjXJMsQbDGx8Ze+3hhfGAPOR0H+fvsotn6KgfW6HwsWYwPYn8HYUxllPz4/8R3tGmXicaULJgeBllwyKMCcljYKFEAZTNhu+WQTunUXZTfbCGkaN6airczfFf8EGV3Rw78TnCHmuE2WYRs8ndpgcnotOyGOU4FA61oeyF6wRisqXeJhyvwuXnULbOnECgHpgifvm7gEEtZAzk4uli23VRW8991oo0XyIBnahWLv+CohFcQSPuaScoMPpeQIDAQAB"

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
    # NOTE: HTML uses the same name/id for organization title and its INN in this local copy;
    # include both candidates so the function can find the available element.
    'training_org_inn': 'OrganizationTitle',
    'knowledge_result': 'IsPassed',
    'knowledge_check_date': 'TestDate',
    'protocol_number': 'ProtocolNumber',
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