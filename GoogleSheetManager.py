import csv
import json

import gspread
from gspread import utils
from google.oauth2.service_account import Credentials

"""This class is for handling the WrongWorksheetException exception"""


class WrongWorksheetException(Exception):
    pass


"""This class is for handling the GoogleSheetManager object"""


class GoogleSheetManager:

    def __init__(self, sheet_name):
        """Constructor"""
        self.client = self.authenticate()
        self.spreadsheet = self.client.open_by_key(self.get_spreadsheet_key())
        self.worksheet = self.spreadsheet.worksheet(sheet_name)

    @staticmethod
    def authenticate():
        """This function authenticate to the Google API"""
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        return gspread.authorize(creds)

    @staticmethod
    def get_spreadsheet_key():
        """This function get the spreadsheet key from the credentials.json file"""
        with open("credentials.json", 'r', encoding='utf-8') as file:
            json_content = json.load(file)
            return json_content["spreadsheet_key"]

    def export_worksheet_to_csv(self, filename):
        """This function export the worksheet to a csv file"""
        export_data = self.worksheet.get_all_values()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(export_data)

    def update_worksheet_with_csv(self, filename):
        """This function update the worksheet with a csv file"""
        self.spreadsheet.values_update(
            self.worksheet.title,
            params={'valueInputOption': 'USER_ENTERED'},
            body={'values': list(csv.reader(open(filename, encoding='utf-8')))}
        )

    def get_round(self):
        """This function get the current round"""
        if self.worksheet.title != "Algo V3":
            raise WrongWorksheetException
        else:
            return self.worksheet.acell('H1').value

    def update_csv(self, filename, current_round, team_match_and_trust_rate, score):
        """This function update the csv file with the new data passed in parameters"""

        # This has to be modified every season
        team_name_which_cause_issues = ["SÜPREME", "SÜPREME²", "EMPIRΞ", "EMPIRΞ²", "EMPIRΞ³", "Project GER",
                                        "Project GER²", "Project GER³", "UNIVERSE™", "UNIVERSE™²", "Swedish Power",
                                        "Swedish Power⁴", "UNIÓN~H", "UNIÓN~H²", "MADE !N FORCE", "MADE !N FORCE²",
                                        "French Spirit¹", "French Spirit²", "French Spirit³", "Discord", "Discord²",
                                        "B R A Z I L ¹"]

        # Check if the team is not in the list of teams which cause issues and if the trust rate is above 20%
        if team_match_and_trust_rate[0] not in team_name_which_cause_issues \
                and team_match_and_trust_rate[1] >= 20:

            # Get content
            rows = self.get_csv_content(filename)

            # Get team name with emote thanks to team association json file
            with open("assets/files/Season_26/Season-26_teams_association.json", 'r', encoding='utf-8') as file:
                json_content = json.load(file)
            team_name_with_emote = json_content[team_match_and_trust_rate[0]]

            # Get column and row index based on the round
            column_index = self.get_column_index(rows, "rnd" + current_round)
            row_index = self.get_row_index(rows, team_name_with_emote)

            if row_index is not None and column_index is not None:
                rows[row_index][column_index] = int(score)

            with open(filename, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)

    def update_worksheet_batch(self, current_round):
        # Get content
        rows = self.get_csv_content("assets/files/exported_top_100_csv.csv")

        # Get values from rows only from column current_round
        column_index = self.get_column_index(rows, "rnd" + current_round)

        scores_values = []
        for row in rows:
            if row[column_index] != "rnd" + current_round and row[column_index] != "":
                scores_values.append([int(row[column_index])])
            else:
                scores_values.append([row[column_index]])

        # Get the letter concerned
        start_letter_scores = utils.rowcol_to_a1(1, column_index + 1)
        end_letter_scores = utils.rowcol_to_a1(101, column_index + 1)

        self.worksheet.batch_update([
            {
                'range': f'{start_letter_scores}:{end_letter_scores}',
                'values': scores_values,
            }])

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
            if row[2] == team_name_with_emote:
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
            if column_index - 1 >= 0:
                if int(rows[row_index][column_index - 1]) + 4353 >= int(score) >= int(
                        rows[row_index][column_index - 1]):
                    return True
                else:
                    return False
            else:
                return False

    def get_opponent(self, team_name, current_round):
        # Get content
        rows = self.get_csv_content("assets/files/exported_csv.csv")

        # Get column index based on the round
        column_index = self.get_column_index(rows, current_round)

        # Get row index based on the team name
        row_index = self.get_row_index(rows, team_name)

        if row_index is not None and column_index is not None:
            return rows[row_index][column_index + 1]
        else:
            return None
