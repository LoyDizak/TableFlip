from backend.data import Person
import shutil
import textwrap


def matrix_to_string(table, max_width=120, padding=1):
    """
    Принимает двумерный список (таблица) и возвращает
    аккуратно форматированное строковое представление таблицы
    с учётом ширины консоли.
    """

    if not table or not any(table):
        return "Пустая таблица"

    columns = len(table[0])
    usable_width = max_width - (columns + 1)
    col_width = max(5, usable_width // columns)

    wrapped_table = []
    for row in table:
        wrapped_row = [
            textwrap.wrap(str(cell), col_width - padding * 2) or [""]
            for cell in row
        ]
        wrapped_table.append(wrapped_row)

    row_heights = [max(len(cell) for cell in row) for row in wrapped_table]
    horizontal = "+" + "+".join(["-" * col_width] * columns) + "+"

    lines = [horizontal]

    for row, height in zip(wrapped_table, row_heights):
        for i in range(height):
            line = "|"
            for cell in row:
                text = cell[i] if i < len(cell) else ""
                line += text.center(col_width) + "|"
            lines.append(line)
        lines.append(horizontal)

    return "\n".join(lines)


def person_to_string(person: Person) -> str:
    """
    Возвращает личную информацию из объекта Person
    в аккуратно отформатированном виде.
    """

    def line(label: str, value: str) -> str:
        return f"{label:<25}: {value or '[-]'}"

    lines = [
        line("Полное имя", person.full_name),
        line("Фамилия", person.last_name),
        line("Имя", person.first_name),
        line("Отчество", person.middle_name),
        line("СНИЛС", person.snils),
        line("Профессия (должность)", person.position),
        line("Место работы", person.workplace),
        line("ИНН работодателя", person.workplace_inn),
        line("Программа обучения", person.training_program),
        line("Организация обучения", person.training_org),
        line("ИНН организации обучения", person.training_org_inn),
        line("Результат проверки знаний", person.knowledge_result),
        line("Дата проверки знаний", person.knowledge_check_date),
        line("Номер протокола", person.protocol_number),
    ]

    return "\n".join(lines)


def person_to_string_new(person: dict) -> str:
    """
    Возвращает личную информацию из объекта Person
    в аккуратно отформатированном виде.
    """

    lines = []

    for field in person.values():
        lines.append(f"{field["name"]:<25}: {field["value"] or '[-]'}")

    return "\n".join(lines)


def persons_list_to_string(persons: list[Person]) -> str:
    all_persons = ""
    for person in persons:
        all_persons += person_to_string(person)
        all_persons  += "\n\n"
    return all_persons


def persons_list_to_string_new(persons: list[dict]) -> str:
    all_persons = ""
    for person in persons:
        all_persons += person_to_string_new(person)
        all_persons  += "\n\n"
    return all_persons
