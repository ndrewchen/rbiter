from googleapiclient.discovery import build
from credentials import get_credentials
from grader import grade_column

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sheet_id = '1NxwMbKl6d77dcvQa-jSvg_PF6oomb9JYQidgQMJlWSo'
    # https://docs.google.com/spreadsheets/d/1NxwMbKl6d77dcvQa-jSvg_PF6oomb9JYQidgQMJlWSo/

    # DO NOT MODIFY
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # test 1
    correct = '\\frac{88}{379}'
    grade_column(sheet, sheet_id, correct, 'rbiter!A2:A643', 'rbiter!B2:B643', mode='symbolic')