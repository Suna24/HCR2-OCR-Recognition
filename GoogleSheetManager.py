import csv
import json

import gspread
from google.oauth2.service_account import Credentials


class WrongWorksheetException(Exception):
    pass


class GoogleSheetManager:

    def __init__(self, sheet_name):
        self.client = self.authenticate()
        self.spreadsheet = self.client.open_by_key(self.get_spreadsheet_key())
        self.worksheet = self.spreadsheet.worksheet(sheet_name)

    @staticmethod
    def authenticate():
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        return gspread.authorize(creds)

    def get_spreadsheet_key(self):
        with open("credentials.json", 'r', encoding='utf-8') as file:
            json_content = json.load(file)
            return json_content["spreadsheet_key"]

    def export_worksheet_to_csv(self, filename):
        export_data = self.worksheet.get_all_values()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(export_data)

    def update_worksheet_with_csv(self, filename):
        self.spreadsheet.values_update(
            self.worksheet.title,
            params={'valueInputOption': 'USER_ENTERED'},
            body={'values': list(csv.reader(open(filename, encoding='utf-8')))}
        )

    def get_round(self):
        if self.worksheet.title != "Algo V3":
            raise WrongWorksheetException
        else:
            return self.worksheet.acell('H1').value

    def update_csv(self, filename, current_round, tesseract_team_name_detected, team_match_and_trust_rate, score):
        # Get content
        rows = self.get_csv_content(filename)

        # Get column index based on the round
        column_index = None
        if rows and len(rows[0]) > 0:
            column_index = rows[0].index(current_round)

        # Get team name with emote thanks to team association json file
        with open("assets/files/teams_association.json", 'r', encoding='utf-8') as file:
            json_content = json.load(file)

        team_name_with_emote = json_content[team_match_and_trust_rate[0]]

        # Get row index based on the team name
        row_index = None
        for i, row in enumerate(rows):
            if row[0] == team_name_with_emote:
                row_index = i
                break

        if row_index is not None and column_index is not None:
            rows[row_index][column_index] = tesseract_team_name_detected
            rows[row_index][column_index + 1] = team_match_and_trust_rate[1]
            rows[row_index][column_index + 2] = score

        # Write the updated rows back to the CSV file
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    @staticmethod
    def get_csv_content(filename):
        rows = []
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)

        return rows
