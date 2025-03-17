from gspread import Client, Spreadsheet, Worksheet, service_account


def client_init_json() -> Client:
    """Создание клиента для работы с Google Sheets."""
    return service_account(filename='postlink-454012-9c405e1ac6a1.json')

print(client_init_json())


def get_table_by_url(client: Client, table_url):
    """Получение таблицы из Google Sheets по ссылке."""
    return client.open_by_url(table_url)


def get_table_by_id(client: Client, table_url):
    """Получение таблицы из Google Sheets по ID таблицы."""
    return client.open_by_key(table_url)



def test_get_table(table_url: str, table_key: str):
    """Тестирование получения таблицы из Google Sheets."""
    client = client_init_json()
    table = get_table_by_url(client, table_url)
    print('Инфо по таблице по ссылке: ', table)
    table = get_table_by_id(client, table_key)
    print('Инфо по таблице по id: ', table)


table_link = 'https://docs.google.com/spreadsheets/d/132WLWR8RwRyRPGgm18fJILhi7hpCsc2NUfIrySlUHWo'
table_id = '132WLWR8RwRyRPGgm18fJILhi7hpCsc2NUfIrySlUHWo'

def get_worksheet_info(table: Spreadsheet) -> dict:
    """Возвращает количество листов в таблице и их названия."""
    worksheets = table.worksheets()
    worksheet_info = {
        "count": len(worksheets),
        "names": [worksheet.title for worksheet in worksheets]
    }
    return worksheet_info


def main():
    # Создаем клиента и открываем таблицу
    client = client_init_json()
    table = get_table_by_id(client, table_id)

    # Получаем информацию о листах
    info = get_worksheet_info(table)
    print(f"Количество листов: {info['count']}")
    print("Названия листов:")
    for name in info['names']:
        print(name)


def insert_one(table: Spreadsheet, title: str, data: list, index: int = 1):
    """Вставка данных в лист."""
    worksheet = table.worksheet(title)
    res = worksheet.insert_row(data, index=index)
    print(res)


def test_add_data():
    """Тестирование добавления данных в таблицу."""
    client = client_init_json()
    table = get_table_by_id(client, table_id)
    worksheet_info = get_worksheet_info(table)
    print('Инфо по таблице: ', worksheet_info)
    insert_one(table=table,
               title=worksheet_info['names'][0],
               data=['name', 'address', 'email', 'phone_number', 'birth_date', 'company', 'job'])


test_add_data()