import os
import os.path
import json
import logging
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("SHEET_ID")
SAMPLE_RANGE_NAME = os.getenv("SHEET_RANGE")

logging.getLogger().setLevel(logging.INFO)

class Bookmark:
    """
    Bookmark for OWRX
    """
    name: str
    frequency: str
    modulation: str
    
    def __init__(self, name: str, freq: str, mode: str) -> None:
        self.name = name
        self.frequency = int(float(freq.replace(",", ".")) * 1000000)
        self.modulation = mode.upper()

def bookmarks_list_to_json(bookmarks_list: list[Bookmark]) -> str:
    """
    From list to JSON

    Args:
        bookmarks_list (list[Bookmark]): list of bookmarks from class

    Returns:
        str: JSON payload
    """
    bookmarks_json = []
    for bookmark in bookmarks_list:
        bookmark_json = {
            "name": bookmark.name,
            "frequency": bookmark.frequency,
            "modulation": bookmark.modulation
        }
        bookmarks_json.append(bookmark_json)
    return json.dumps(bookmarks_json, indent=4)

def sheets_to_owrx():
    """
    Authenticates with Google to get a Sheet
    and exports the content to a JSON file
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if not os.path.exists("input"):
            os.makedirs("input")
    if os.path.exists("./input/token.json"):
        creds = Credentials.from_authorized_user_file("./input/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("./input/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("./input/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            logging.warning("No data found.")
            return

        bookmarks: list[Bookmark] = []

        for row in values:
            logging.info("Found bookmark: %s, %s, %s", row[7], row[0], row[8])
            bookmark = Bookmark(row[7], row[0], row[8])
            bookmarks.append(bookmark)

        json_data = bookmarks_list_to_json(bookmarks)
        if not os.path.exists("output"):
            os.makedirs("output")
        with open("./output/bookmarks.json", 'w', encoding="UTF-8") as file:
            file.write(json_data)

    except HttpError as err:
        logging.error("Cannot get data from Google Sheets, error: %s", err)

def main():
    """
    Fetch data every 15 minutes from Google Sheets and sends it to OWRX
    """
    while True:
        sheets_to_owrx()
        time.sleep(60  * 15)  # Waiting 15 minutes before next request to avoid DDo

if __name__ == "__main__":
    main()
