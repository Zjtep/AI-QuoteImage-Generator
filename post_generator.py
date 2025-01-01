from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageEnhance
import textwrap
import os
import re

class ImageQuoteGenerator:
    def __init__(self, image_dir, quotes_file, output_dir, logo_path=None, platform='instagram_post'):
        self.image_dir = image_dir
        self.quotes_file = quotes_file
        self.output_dir = output_dir
        self.logo_path = logo_path
        self.platform = platform
        self.images = self.get_im_paths()
        self.quotes = self.get_quotes()

        # Set resolution for different platforms
        self.platform_resolutions = {
            'instagram_post': (1080, 1080),  # Square (1:1)
            'tiktok': (1080, 1920),  # Vertical (9:16)
        }

    def apply_tint(self, im, tint_color=(200, 200, 200)):
        tinted_im = ImageChops.multiply(im.convert('RGB'), Image.new('RGB', im.size, tint_color))
        return ImageEnhance.Brightness(tinted_im).enhance(1.2)

    def place_logo(self, bkg, logo):
        logo = logo.convert('RGBA') if logo.mode != 'RGBA' else logo
        logo_alpha = logo.split()[3]  # Extract alpha channel
        logo_width, logo_height = logo.size
        bkg_width, bkg_height = bkg.size

        # Position logo in the top-right corner (adjust to your desired corner)
        x_position = bkg_width - logo_width - 10  # 10px padding from the right edge
        y_position = 10  # 10px padding from the top edge

        # Paste the logo onto the background image using alpha for transparency
        bkg.paste(logo, (x_position, y_position), logo_alpha)
        return bkg

    def place_quote_with_rectangle_background(self, im, quote, font):
        draw = ImageDraw.Draw(im)
        W, H = im.size

        # Wrap the text into multiple lines
        lines = textwrap.wrap(quote, width=24)

        # Calculate total height of all lines combined and max width of the lines
        total_height = 0
        max_width = 0  # Track the maximum width of the text lines
        for line in lines:
            bbox_line = draw.textbbox((0, 0), line, font=font)
            total_height += bbox_line[3] - bbox_line[1]  # Height of each line
            max_width = max(max_width, bbox_line[2] - bbox_line[0])  # Max width of lines

        # Set padding to ensure there's space around the text inside the rectangle
        padding = 20  # Padding around the text (adjust as needed)

        # Now place the rectangle correctly based on the calculated values
        rect_left = (W - max_width) // 2 - padding  # Horizontal center of the rectangle with padding

        # Forcefully move the rectangle lower by a fixed number
        rect_top = (H // 4) + 100  # Adjust this number to move the rectangle down
        rect_right = rect_left + max_width + padding * 2  # Adjust for the padding
        rect_bottom = rect_top + total_height + padding  # Adjust the bottom based on text height

        # Ensure the rectangle is within the bounds of the image
        rect_top = max(rect_top, 0)
        rect_bottom = min(rect_bottom, H)

        # Debugging: Print rectangle coordinates to ensure the new position is applied
        print(f"Rectangle Coordinates - Top: {rect_top}, Bottom: {rect_bottom}")
        print(f"Left: {rect_left}, Right: {rect_right}")

        # Draw the black rectangle as the background (it will surround the text now)
        draw.rectangle([rect_left, rect_top, rect_right, rect_bottom], fill='black')

        # Place the lines of the quote one on top of the other, inside the rectangle
        current_h = rect_top + padding-22 # Start placing text at the top of the rectangle
        for line in lines:
            bbox_line = draw.textbbox((0, 0), line, font=font)
            w_line, h_line = bbox_line[2] - bbox_line[0], bbox_line[3] - bbox_line[1]

            # Draw the actual text (white or other color)
            draw.text(((W - w_line) / 2, current_h), line, font=font, fill='white')  # Center text horizontally

            current_h += h_line  # Move down for the next line

    def get_im_paths(self):
        return [f for f in os.listdir(self.image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    def get_quotes(self):
        with open(self.quotes_file) as f:
            return [line.strip() for line in f.readlines()]

    def resize_and_crop_image_for_platform(self, im):
        width, height = self.platform_resolutions.get(self.platform, (1080, 1080))
        original_width, original_height = im.size

        if original_width / original_height > width / height:
            new_width = width * 2
            new_height = int((new_width / original_width) * original_height)
        else:
            new_height = height * 2
            new_width = int((new_height / original_height) * original_width)

        im = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        right = left + width
        bottom = top + height
        im = im.crop((left, top, right, bottom))

        return im

    def build_image(self, im_path, quote, im_count, logoify=True):
        im = Image.open(im_path)
        im = self.resize_and_crop_image_for_platform(im)
        font = ImageFont.truetype("utils/BebasNeue.otf", 80)

        self.place_quote_with_rectangle_background(im, quote, font)

        if logoify and self.logo_path:
            logo = Image.open(self.logo_path)
            self.place_logo(im, logo)

        platform_resolution = self.platform_resolutions.get(self.platform, (1080, 1080))
        width, height = platform_resolution
        sanitized_quote = re.sub(r'[\\/*?:"<>|]', "", quote)[:40]
        sanitized_image_name = os.path.splitext(os.path.basename(im_path))[0]
        output_filename = f"{sanitized_image_name}_{width}x{height}_{sanitized_quote}.png"
        output_path = os.path.join(self.output_dir, output_filename)

        im.save(output_path)
        print(f"Output image saved as: {output_path}")

    def generate_images(self, combos=True, logoify=True):
        im_count = 0
        for im_path in self.images:
            for quote in self.quotes:
                print(f"Overlaying {im_path} with quote: {quote}...")
                self.build_image(os.path.join(self.image_dir, im_path), quote, im_count, logoify)
                im_count += 1

def main():
    image_dir = "in/raw"
    quotes_file = "in/quotes.txt"
    output_dir = "out"
    logo_path = "utils/logopy_tiny.png"
    platforms = ['instagram_post', 'tiktok']
    combos = input("Generate all combinations? (y/n): ") == 'y'
    logoify = input("Include logo? (y/n): ") == 'y'

    for platform in platforms:
        print(f"Generating images for {platform}...")
        generator = ImageQuoteGenerator(image_dir, quotes_file, output_dir, logo_path, platform)
        generator.generate_images(combos, logoify)
        print(f"Finished generating images for {platform}\n")

if __name__ == '__main__':
    main()
