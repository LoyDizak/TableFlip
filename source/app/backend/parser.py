from docx import Document
import logging

from backend.data import TableLayout, Person




def parse_table_data(table: list[list[str]], table_layout: TableLayout, start_row: int = 0) -> list[Person]:
    """
    Извлекает персональные данные из таблицы (двумерного списка)
    в список объектов Person на основе TableLayout.
    """

    persons = []

    def get_cell(index: int) -> str:
        """Возвращает значение ячейки или пустую строку, если индекс -1 или вне диапазона."""
        if index >= len(row):
            raise
        if index < 0:
            return ""
        return row[index].strip()

    for row in table[start_row:]:
        person = Person(
            full_name=get_cell(table_layout.full_name),
            last_name= "",
            first_name= "",
            middle_name= "",
            snils=get_cell(table_layout.snils),
            position=get_cell(table_layout.position),
            workplace=get_cell(table_layout.workplace),
            workplace_inn=get_cell(table_layout.workplace_inn),
            training_program=get_cell(table_layout.training_program),
            training_org=get_cell(table_layout.training_org),
            training_org_inn=get_cell(table_layout.training_org_inn),
            knowledge_result=get_cell(table_layout.knowledge_result),
            knowledge_check_date=get_cell(table_layout.knowledge_check_date),
            protocol_number=get_cell(table_layout.protocol_number)
        )

        split_name = person.full_name.split(" ")
        if len(split_name) == 3:
            person.last_name = split_name[0]
            person.first_name = split_name[1]
            person.middle_name = split_name[2]
        # else:
        #     logging.error(f"Не получилось разделить ФИО на составляющие: {person.full_name}")

        persons.append(person)

    return persons


def add_data_to_persons_list(persons_list: list[Person], data_type:str, data: str):
    logging.info(f"Добавляю поле \"{data_type}\" ко всем записям")
    if not hasattr(persons_list[0], data_type):
        logging.error(f"Поле \"{data_type}\" не найдено")
        return
    
    for person in persons_list:
        setattr(person, data_type, data)
 

def extract_docx_table(docx_path: str, table_index: int):
    """
    Открывает Word-файл по пути docx_path,
    выбирает таблицу с номером table_index (0-based),
    и возвращает её содержимое как двумерный список строк.
    """
    logging.info(f"Начинаю парсинг docx файла по пути: \"{docx_path}\"")
    logging.info(f"Ищу таблицу под индексом: {table_index}")

    doc = Document(docx_path)
    all_tables = doc.tables

    if table_index < 0 or table_index >= len(all_tables):
        logging.error(f"Таблица с индексом {table_index} не найдена")
        return

    table = all_tables[table_index]

    result = []
    for row in table.rows:
        row_data = []
        for cell in row.cells:
            row_data.append(cell.text)
        result.append(row_data)

    return result
