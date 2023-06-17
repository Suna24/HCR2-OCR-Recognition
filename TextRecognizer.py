import re

import pytesseract
import cv2
from pytesseract import Output


class TextRecognizer:
    def __init__(self, image):
        self.image = image

    def draw_rectangles(self):
        h, w, c = self.image.shape
        boxes = pytesseract.image_to_boxes(self.image)

        for b in boxes.splitlines():
            b = b.split(' ')
            image_with_rect = cv2.rectangle(self.image, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])),
                                            (0, 255, 0), 2)

        return image_with_rect

    def get_dictionary(self):
        dictionary = pytesseract.image_to_data(self.image, output_type=Output.DICT)
        return dictionary

    def get_raw_text(self):
        raw_text = pytesseract.image_to_string(self.image, config=r'--oem 3 --psm 12 --user-words eng.user-words',
                                               lang='eng+grc+rus')
        return raw_text

    def get_json_text(self):
        lines = self.get_raw_text().split('\n')

        # Remove empty lines
        lines = list(filter(None, lines))

        # Remove lines that contains only one character
        lines = list(filter(lambda x: len(x) > 1, lines))

        # Group lines by pairs (because sometimes, score is before the team name and vice versa)
        lines = [lines[i:i + 2] for i in range(0, len(lines), 2)]

        self.apply_correction(lines)

        data = []

        print(lines)

        for line in lines:
            if self.string_contains_only_digits_and_spaces(line[0]):
                data.append({"team": line[1], "score": line[0].replace(" ", "")})
            elif self.string_contains_only_digits_and_spaces(line[1]):
                data.append({"team": line[0], "score": line[1].replace(" ", "")})

        return data

    def apply_correction(self, lines):
        for line in lines:
            # if the line starts with numbers and ends with S, replace it by 5
            if re.match("^[0-9]+S$", line[0]) and line[0].endswith("S"):
                line[0] = line[0].replace("S", "5")

            if re.match("^[0-9]+S$", line[1]) and line[1].endswith("S"):
                line[1] = line[1].replace("S", "5")

    @staticmethod
    def string_contains_only_digits_and_spaces(string):
        if re.match("^[0-9 ]+$", string):
            return True
        else:
            return False


