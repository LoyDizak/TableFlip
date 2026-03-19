from docx import Document


def parse_table_data(table: list[list[str]], person_template: dict, start_row: int = 0) -> list[dict]:
    persons = []

    for row in table[start_row:]:
        person = {}
        for field, mapping in person_template.items():
            column_index: int = mapping["column_index"]
            if column_index < 0:
                person[field] = ""
            elif column_index < len(row):
                person[field] = row[column_index].strip()
            else:
                raise

        split_name = person["full_name"].split(" ")
        if len(split_name) == 3:
            person["last_name"] = split_name[0]
            person["first_name"] = split_name[1]
            person["middle_name"] = split_name[2]
        persons.append(person)

    return persons


def add_data_to_persons_list(persons_list: list[dict], data_type:str, data: str): 
    for person in persons_list:
        if data_type in person.keys():
            person[data_type] = data
 

def extract_docx_table(docx_path: str, table_index: int) -> list[list[str]]:
    doc = Document(docx_path)
    all_tables = doc.tables

    if table_index < 0 or table_index >= len(all_tables):
        return [[""]]

    table = all_tables[table_index]

    result = []
    for row in table.rows:
        row_data = []
        for cell in row.cells:
            row_data.append(cell.text)
        result.append(row_data)

    return result