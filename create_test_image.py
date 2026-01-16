"""
Script to generate a sample profile image for testing.
"""
from PIL import Image, ImageDraw, ImageFont
import os


def create_profile_image():
    """Create a simple profile image for testing purposes."""
    # Create a 200x200 image with a gradient background
    img = Image.new('RGB', (200, 200), color='#4A90E2')
    
    # Draw a circle in the center
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], fill='#FFFFFF', outline='#2E5C8A', width=3)
    
    # Draw initials in the center
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw text
    text = "JD"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((200 - text_width) // 2, (200 - text_height) // 2 - 10)
    draw.text(position, text, fill='#4A90E2', font=font)
    
    # Save the image
    output_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'profile_image.png')
    img.save(output_path)
    print(f"Profile image created at: {output_path}")


if __name__ == "__main__":
    create_profile_image()
