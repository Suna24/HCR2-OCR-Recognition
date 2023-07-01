from ImageProcessor import ImageProcessor
from TextRecognizer import TextRecognizer
from TeamAnalyzer import TeamAnalyzer
from GoogleSheetManager import GoogleSheetManager

# This is for getting the current round only
google_sheet_manager_algo_v3 = GoogleSheetManager('Algo V3')

# Specify here all images paths to process
leaderboard_paths = [
    "assets/images/leaderboard_1.png",
    "assets/images/leaderboard_2.png",
    "assets/images/leaderboard_3.png",
    "assets/images/leaderboard_4.png",
    "assets/images/leaderboard_5.png",
    "assets/images/leaderboard_6.png",
    "assets/images/leaderboard_7.png",
    "assets/images/leaderboard_8.png",
    "assets/images/leaderboard_9.png",
    "assets/images/leaderboard_10.png",
    "assets/images/leaderboard_11.png",
]

# Replace the file here according to the season
team_analyzer = TeamAnalyzer("assets/files/Season_26/Season-26_teams_without_emotes.txt")

google_sheet_manager_top_100 = GoogleSheetManager('Top 100 api suna')

# We get the csv file from the sheet
google_sheet_manager_top_100.export_worksheet_to_csv("assets/files/exported_top_100_csv.csv")

for path in leaderboard_paths:
    # Process the image to be ready for tesseract
    image_processor = ImageProcessor(path)
    image_processor.process_image()

    # Tesseract object
    text_recognizer = TextRecognizer(image_processor.image)

    # Get the json text
    for obj in text_recognizer.get_json_text():
        print(obj["team"], obj["score"], team_analyzer.find_most_probable_team_matches_fuzz_algorithm(obj["team"]), sep=": ")

        # We update the csv file with the new data
        google_sheet_manager_top_100.update_csv(filename="assets/files/exported_top_100_csv.csv",
                                                current_round=google_sheet_manager_algo_v3.get_round(),
                                                team_match_and_trust_rate=team_analyzer.find_most_probable_team_matches_fuzz_algorithm(obj["team"])[0],
                                                score=obj["score"])

# We update the sheet with the new data
google_sheet_manager_top_100.update_worksheet_batch(google_sheet_manager_algo_v3.get_round())
