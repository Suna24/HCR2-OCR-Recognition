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
            # Here return the round for which you want to enter the results (it can be a command argument maybe)
            return "4"
            # In the case of the Algo V3 worksheet, the round is in the cell H1
            # return self.worksheet.acell('H1').value

    def update_csv(self, filename, current_round, team_match_and_trust_rate, score):
        """This function update the csv file with the new data passed in parameters"""

        # This has to be modified every season
        team_name_which_cause_issues = ["E M P I R Ξ", "E M P I R Ξ²", "E M P I R Ξ³",
                                        "RPS",
                                        "Project GER", "Project GER²", "Project GER³",
                                        "Low||Lands", "Low Lands 2",
                                        "PERSIA", "P E R S I A™",
                                        "Sharks", "Sharks²",
                                        "Ñ&FRIENDS", "Ñ&FRIENDS²",
                                        "MADE !N FORCE", "MADE !N FORCE3"]

        # Check if the team is not in the list of teams which cause issues and if the trust rate is above 40%
        if team_match_and_trust_rate[0] not in team_name_which_cause_issues \
                and team_match_and_trust_rate[1] >= 40:

            # Get content
            rows = self.get_csv_content(filename)

            # Get team name with emote thanks to team association json file
            with open("assets/files/Season_27/Season-27_teams_association.json", 'r', encoding='utf-8') as file:
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
        """This function get the content of a csv file"""
        rows = []
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)

        return rows

    @staticmethod
    def get_column_index(rows, current_round):
        """This function get the column index based on the round"""
        column_index = None
        if rows and len(rows[0]) > 0:
            column_index = rows[0].index(current_round)

        return column_index

    @staticmethod
    def get_row_index(rows, team_name_with_emote):
        """This function get the row index based on the team name"""
        row_index = None
        for i, row in enumerate(rows):
            if row[2] == team_name_with_emote:
                row_index = i
                break
        return row_index
