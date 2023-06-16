from PIL import Image


class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)

    def swap_colors(self):
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
        self.crop_image()
        self.image.save(self.image_path.replace('.png', '_cropped.png'))
        self.swap_colors()
        self.image.save(self.image_path.replace('.png', '_ready_for_tesseract.png'))

    def crop_image(self):
        self.image = self.image.crop(((self.image.width / 2.6), 370, (self.image.width / 1.2), self.image.height))

    @staticmethod
    def is_pixel_considered_white(r, g, b):
        return r > 230 and g > 230 and b > 230
