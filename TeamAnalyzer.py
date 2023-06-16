from fuzzywuzzy import fuzz
from jellyfish import jaro_winkler_similarity


class TeamAnalyzer:
    def __init__(self, season_teams_path):
        self.teams_list = self.load_teams_from_file(season_teams_path)

    @staticmethod
    def load_teams_from_file(file_path):
        with open(file_path, 'r', encoding="utf8") as file:
            return file.read().splitlines()

    def find_most_probable_team_matches_fuzz_algorithm(self, team_name):
        most_probable_teams = []

        for team in self.teams_list:
            ratio = fuzz.ratio(team_name, team)
            most_probable_teams.append([team, ratio])

        # Sort the list by the ratio
        most_probable_teams.sort(key=lambda x: x[1], reverse=True)

        return most_probable_teams

    def find_most_probable_team_matches_jaro_winkler(self, team_name):
        most_probable_teams = []

        for team in self.teams_list:
            similarity = jaro_winkler_similarity(team_name, team)
            most_probable_teams.append([team, similarity])

        # Sort the list by the similarity in descending order
        most_probable_teams.sort(key=lambda x: x[1], reverse=True)

        return most_probable_teams

