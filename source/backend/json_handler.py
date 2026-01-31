import json
from dataclasses import asdict

from backend.data import Person

def save_persons_to_json(file_path: str, persons: list[Person]) -> None:
    data = [asdict(person) for person in persons]

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def load_persons_from_json(file_path: str) -> list[Person]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    persons = []
    for item in data:
        person = Person(**item)
        persons.append(person)

    return persons