# GoogleSheetsToOpenwebrxBookmarks

Simple script to create OpenWebRx bookmarks from a Google Sheet document

## Usage

1. Create an authentication token by following [this guide](https://developers.google.com/sheets/api/quickstart/python?hl=it)
1. Copy the `credentials.json` to the `./input` folder
1. Execute the script on your laptop to make the first authentication
1. Create a Google Sheet where:
    - Column `A` is the frequency in MHz with comma separator (e.g: `144,300000`)
    - Column `H` is the bookmark name
    - Column `I` is the bookmark mode
1. Launch the container
    - Map the `./input/` folder anywhere on your device  (e.g., `/home/user/input`)
    - Map the `./output` folder to `/var/lib/openwebrx` (where bookmarks are stored)
    - Set `SHEET_ID` to the ID of the Google Sheet you want to read
    - Set `SHEET_RANGE` to the cells range of the Google Sheet you want to access (e.g: `Class Data!A2:E`)
