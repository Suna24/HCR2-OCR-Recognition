from ImageProcessor import ImageProcessor
from TextRecognizer import TextRecognizer
from TeamAnalyzer import TeamAnalyzer
from GoogleSheetManager import GoogleSheetManager

google_sheet_manager = GoogleSheetManager('update api suna')
google_sheet_manager.export_worksheet_to_csv("assets/files/exported_csv.csv")

google_sheet_manager_algo_v3 = GoogleSheetManager('Algo V3')

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

team_analyzer = TeamAnalyzer("assets/files/Season-26_teams_without_emotes.txt")

for path in leaderboard_paths:
    image_processor = ImageProcessor(path)
    image_processor.process_image()

    text_recognizer = TextRecognizer(image_processor.image)

    for obj in text_recognizer.get_json_text():
        print(obj["team"], obj["score"], team_analyzer.find_most_probable_team_matches_fuzz_algorithm(obj["team"]), sep=": ")
        google_sheet_manager.update_csv(filename="assets/files/exported_csv.csv",
                                        current_round=google_sheet_manager_algo_v3.get_round(),
                                        tesseract_team_name_detected=obj["team"],
                                        team_match_and_trust_rate=team_analyzer.find_most_probable_team_matches_fuzz_algorithm(obj["team"])[0],
                                        score=obj["score"])

google_sheet_manager.update_worksheet_batch(google_sheet_manager_algo_v3.get_round())
