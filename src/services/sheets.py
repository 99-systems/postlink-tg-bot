import json
from gspread import Client, Spreadsheet, service_account_from_dict


from src.config import config
from src.database.models.user import User
from src.database.models.request import DeliveryRequest, SendRequest


def client_init_json() -> Client:
    creds = json.loads(config.SERVICE_ACCOUNT_CREDS)
    return service_account_from_dict(creds)


def get_table(client: Client, table_url: str = config.GOOGLE_SHEETS_API_KEY) -> Spreadsheet:
    return client.open_by_key(table_url)



def get_worksheet_info(table: Spreadsheet) -> dict:
    worksheets = table.worksheets()
    worksheet_info = {
        "count": len(worksheets),
        "names": [worksheet.title for worksheet in worksheets]
    }
    return worksheet_info


def record_add_user(user: User):
    try:
        client = client_init_json()
        table = get_table(client)
        worksheet = table.worksheet('Users')
        data = [user.id, user.name, user.phone, user.city, user.created_at.isoformat(), '@' + user.telegram_user.username, user.telegram_user.telegram]
        res = worksheet.append_row(data)
    except Exception as e:
        print("record_error: " + str(e))

def record_add_deliver_req(req: DeliveryRequest):
    try:
        client = client_init_json()
        table = get_table(client)
        worksheet = table.worksheet('Deliver requests')
        data = [req.id, str(req.user_id) + '-' + req.user.name, req.from_location, req.to_location, req.delivery_date.isoformat(), req.size_type, req.status, req.created_at.isoformat(), req.updated_at.isoformat()]
        res = worksheet.append_row(data)
    except Exception as e:
        print("record_error: " + str(e))


def record_add_send_req(req: SendRequest):
    try:
        client = client_init_json()
        table = get_table(client)
        worksheet = table.worksheet('Send requests')
        data = [req.id, str(req.user_id) + '-' + req.user.name, req.from_location, req.to_location, req.from_date.isoformat(), req.to_date.isoformat(), req.size_type, req.description, req.status, req.created_at.isoformat(), req.updated_at.isoformat()]
        res = worksheet.append_row(data)
    except Exception as e:
        print("record_error: " + str(e))

def record_close_deliver_req(req_id: int):
    try:
        client = client_init_json()
        table = get_table(client)
        worksheet = table.worksheet('Deliver requests')
        cell = worksheet.find(str(req_id))
        row_number = cell.row 
        worksheet.update_cell(row_number, 7, "closed")
    except Exception as e:
        print("record_error: " + str(e))


def record_close_send_req(req_id: int):
    try:
        client = client_init_json()
        table = get_table(client)
        worksheet = table.worksheet('Send requests')
        cell = worksheet.find(str(req_id))
        row_number = cell.row 
        worksheet.update_cell(row_number, 9, "closed")
    except Exception as e:
        print("record_error: " + str(e))