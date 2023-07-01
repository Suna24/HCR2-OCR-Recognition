from fuzzywuzzy import fuzz

"""This class is responsible for analyzing the team names and finding the most probable matches."""


class TeamAnalyzer:
    def __init__(self, season_teams_path):
        """Constructor"""
        self.teams_list = self.load_teams_from_file(season_teams_path)

    @staticmethod
    def load_teams_from_file(file_path):
        """Load the teams from the file and return a list of teams"""
        with open(file_path, 'r', encoding="utf8") as file:
            return file.read().splitlines()

    def find_most_probable_team_matches_fuzz_algorithm(self, team_name):
        """Find the most probable matches using the fuzz algorithm"""
        most_probable_teams = []

        for team in self.teams_list:
            ratio = fuzz.ratio(team_name, team)
            most_probable_teams.append([team, ratio])

        # Sort the list by the ratio
        most_probable_teams.sort(key=lambda x: x[1], reverse=True)

        return most_probable_teams
