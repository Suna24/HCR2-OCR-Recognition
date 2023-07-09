from ImageProcessor import ImageProcessor
from TextRecognizer import TextRecognizer
from TeamAnalyzer import TeamAnalyzer
from GoogleSheetManager import GoogleSheetManager
import os

# This is for getting the current round only
google_sheet_manager_algo_v3 = GoogleSheetManager('Algo V3')

# Specify here all images paths to process
leaderboard_paths = os.listdir("assets/images/")
# Filter out file paths that end with "cropped" or "ready_for_tesseract"
leaderboard_paths = [path for path in leaderboard_paths if not path.endswith("cropped.png") and not path.endswith("ready_for_tesseract.png")]

# Replace the file here according to the season
team_analyzer = TeamAnalyzer("assets/files/Season_27/Season-27_teams_without_emotes.txt")

# Modify the name of the sheet here (if you want to do test -> Top 100 api suna)
google_sheet_manager_top_100 = GoogleSheetManager('Top 100')

# We get the csv file from the sheet
google_sheet_manager_top_100.export_worksheet_to_csv("assets/files/exported_top_100_csv.csv")

for path in leaderboard_paths:
    # Process the image to be ready for tesseract
    image_processor = ImageProcessor("assets/images/" + path)
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
