from PIL import Image, ImageDraw, ImageFont
import textwrap

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

    # Set the position of the rectangle
    rect_left = (W - max_width) // 2 - padding  # Horizontal center of the rectangle with padding
    rect_top = (H // 5) - padding  # Move the rectangle down (adjust as needed)
    rect_right = rect_left + max_width + padding * 2  # Adjust for the padding
    rect_bottom = rect_top + total_height + padding  # Adjust the bottom based on text height

    # Ensure the rectangle is within the bounds of the image
    rect_top = max(rect_top, 0)
    rect_bottom = min(rect_bottom, H)

    # Draw the black rectangle as the background (it will surround the text now)
    draw.rectangle([rect_left, rect_top, rect_right, rect_bottom], fill='black')

    # Place the lines of the quote one on top of the other, inside the rectangle
    current_h = rect_top + padding  # Start placing text at the top of the rectangle
    for line in lines:
        bbox_line = draw.textbbox((0, 0), line, font=font)
        w_line, h_line = bbox_line[2] - bbox_line[0], bbox_line[3] - bbox_line[1]

        # Draw the actual text (white or other color)
        draw.text(((W - w_line) / 2, current_h), line, font=font, fill='white')  # Center text horizontally

        current_h += h_line  # Move down for the next line

# Example usage
if __name__ == '__main__':
    image_path = 'input_image.jpg'  # Replace with your image path
    output_path = 'output_image.jpg'  # Replace with your desired output path

    im = Image.open(image_path)
    quote = "Your example quote goes here!"

    # Path to your custom font
    font_path = r"D:\NEXTCLOUD\Documents\Code\Motivational-AI-Content-Generator\utils\YourFontName.ttf"  # Update this path

    # Load the font with the desired size
    font = ImageFont.truetype(font_path, 30)  # Use an appropriate font file and size

    place_quote_with_rectangle_background(im, quote, font)
    im.save(output_path)
    print("Image saved as:", output_path)
