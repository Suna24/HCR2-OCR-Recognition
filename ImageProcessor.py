from PIL import Image

"""This class is used to process the image before sending it to tesseract"""


class ImageProcessor:
    def __init__(self, image_path):
        """Constructor of the class"""
        self.image_path = image_path
        self.image = Image.open(image_path)

    def swap_colors(self):
        """This method swaps the colors of the image in order to get only black and white"""
        pixels = self.image.load()

        # Iterate through each pixel
        width, height = self.image.size
        for y in range(height):
            for x in range(width):
                # Get the RGB values of the pixel
                r, g, b = pixels[x, y]

                # Swap the colors
                if self.is_pixel_considered_white(r, g, b):  # White pixel
                    pixels[x, y] = (0, 0, 0)  # Set to black
                else:  # Non-white pixel
                    pixels[x, y] = (255, 255, 255)  # Set to white

    def process_image(self):
        """This method processes the image and save the intermediate steps"""
        self.crop_image()
        self.image.save(self.image_path.replace('.png', '_cropped.png'))
        self.swap_colors()
        self.image.save(self.image_path.replace('.png', '_ready_for_tesseract.png'))

    def crop_image(self):
        """This method crops the image to get only the leaderboard"""
        # Unfortunately, this is absolute crop and this does not handle various screen sizes
        self.image = self.image.crop(((self.image.width / 2.63), 370, (self.image.width / 1.2), self.image.height))

    @staticmethod
    def is_pixel_considered_white(r, g, b):
        """This method checks if the pixel is considered white or not"""
        return r > 230 and g > 230 and b > 230
