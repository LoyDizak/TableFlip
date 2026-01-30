import json
from dataclasses import asdict
from Parser import Person
import logging

def save_persons_to_json(
    file_path: str,
    persons: list[Person],
    ensure_ascii: bool = False,
    indent: int = 4
) -> None:
    """
    Сохраняет список объектов Person в JSON-файл.

    ensure_ascii=False — корректная запись кириллицы
    indent — удобочитаемое форматирование
    """
    
    logging.info(f"Сохраняю новый файл по пути: \"{file_path}\"")
    data = [asdict(person) for person in persons]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=ensure_ascii,
            indent=indent
        )

def load_persons_from_json(file_path: str) -> list[Person]:
    """
    Считывает JSON-файл и возвращает список объектов Person.
    """
    logging.info(f"Открываю файл по пути: \"{file_path}\"")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    persons = []
    for item in data:
        person = Person(**item)
        persons.append(person)

    return persons