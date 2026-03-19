import json

def save_to_json(file_path: str, data) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_from_json(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)