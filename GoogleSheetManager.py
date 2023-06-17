import csv
import json

import gspread
from gspread import utils
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
            return "7"
            # return self.worksheet.acell('H1').value

    def update_csv(self, filename, current_round, tesseract_team_name_detected, team_match_and_trust_rate, score):
        # Get content
        rows = self.get_csv_content(filename)

        # Get team name with emote thanks to team association json file
        # Get team name with emote thanks to team association json file
        with open("assets/files/teams_association.json", 'r', encoding='utf-8') as file:
            json_content = json.load(file)
        team_name_with_emote = json_content[team_match_and_trust_rate[0]]

        # Get column and row index based on the round
        column_index = self.get_column_index(rows, current_round)
        row_index = self.get_row_index(rows, team_name_with_emote)

        if row_index is not None and column_index is not None:
            if self.is_score_coherent(team_name_with_emote, score, current_round):
                rows[row_index][column_index] = tesseract_team_name_detected
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

    @staticmethod
    def get_column_index(rows, current_round):
        column_index = None
        if rows and len(rows[0]) > 0:
            column_index = rows[0].index(current_round)

        return column_index

    @staticmethod
    def get_row_index(rows, team_name_with_emote):
        row_index = None
        for i, row in enumerate(rows):
            if row[0] == team_name_with_emote:
                row_index = i
                break
        return row_index

    def is_score_coherent(self, team_name, score, current_round):
        """ This method checks is the score assigned to the team is coherent with the score of the previous round """
        # Get content
        rows = GoogleSheetManager.get_csv_content("assets/files/exported_csv.csv")

        # Get column index based on the round
        column_index = self.get_column_index(rows, current_round)

        # Get row index based on the team name
        row_index = self.get_row_index(rows, team_name)

        if row_index is not None and column_index is not None:
            if int(rows[row_index][column_index - 1]) + 4353 >= int(score) >= int(rows[row_index][column_index - 1]):
                return True
            else:
                return False
        else:
            return False

    def update_worksheet_batch(self, current_round):
        # Get content
        rows = self.get_csv_content("assets/files/exported_csv.csv")

        # Get values from rows only from column current_round
        column_index = self.get_column_index(rows, current_round)
        tesseract_values = []
        for row in rows:
            tesseract_values.append([row[column_index]])

        scores_values = []
        for row in rows:
            scores_values.append([row[column_index + 2]])

        # Get the letter concerned
        start_letter_tesseract = utils.rowcol_to_a1(1, column_index + 1)
        end_letter_tesseract = utils.rowcol_to_a1(101, column_index + 1)

        start_letter_scores = utils.rowcol_to_a1(1, column_index + 3)
        end_letter_scores = utils.rowcol_to_a1(101, column_index + 3)

        self.worksheet.batch_update([
            {
                'range': f'{start_letter_tesseract}:{end_letter_tesseract}',
                'values': tesseract_values,
            },
            {
                'range': f'{start_letter_scores}:{end_letter_scores}',
                'values': scores_values,
            }])
