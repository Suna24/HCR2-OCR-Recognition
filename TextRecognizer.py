import re

import pytesseract
import cv2
from pytesseract import Output

"""This class is used to recognize text from an image. It uses the pytesseract library."""


class TextRecognizer:
    def __init__(self, image):
        """Constructor"""
        self.image = image

    def get_raw_text(self):
        """
        This function returns the raw text from the image
        The config parameter is used to specify the language and the page segmentation mode
        """
        raw_text = pytesseract.image_to_string(self.image, config=r'--oem 3 --psm 12 --user-words eng.user-words',
                                               lang='eng+grc+rus')
        return raw_text

    def get_json_text(self):
        """This function returns the text from the image in a json format"""
        lines = self.get_raw_text().split('\n')

        # Remove empty lines
        lines = list(filter(None, lines))

        # Remove lines that contains only one character
        lines = list(filter(lambda x: len(x) > 1, lines))

        # Group lines by pairs (because sometimes, score is before the team name and vice versa)
        lines = [lines[i:i + 2] for i in range(0, len(lines), 2)]

        self.apply_correction(lines)

        data = []

        for line in lines:
            if self.string_contains_only_digits_and_spaces(line[0]):
                data.append({"team": line[1], "score": line[0].replace(" ", "")})
            elif self.string_contains_only_digits_and_spaces(line[1]):
                data.append({"team": line[0], "score": line[1].replace(" ", "")})

        return data

    @staticmethod
    def apply_correction(lines):
        """This function applies some corrections to the text"""
        for line in lines:
            # if the line starts with numbers and ends with S, replace it by 5
            if re.match("^[0-9]+S$", line[0]) and line[0].endswith("S"):
                line[0] = line[0].replace("S", "5")

            if re.match("^[0-9]+S$", line[1]) and line[1].endswith("S"):
                line[1] = line[1].replace("S", "5")

    @staticmethod
    def string_contains_only_digits_and_spaces(string):
        """This function checks if a string contains only digits and spaces"""
        if re.match("^[0-9 ]+$", string):
            return True
        else:
            return False
