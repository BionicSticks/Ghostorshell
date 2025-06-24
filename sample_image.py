from PIL import Image, ImageDraw, ImageFont
import os

# Create a sample image with text for testing OCR
def create_sample_image():
    # Create a white background image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a standard font, fallback to default if not available
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add title
    title = "The Future of Artificial Intelligence"
    draw.text((50, 50), title, font=font_large, fill='black')
    
    # Add main content paragraphs
    content = [
        "Artificial intelligence has revolutionized many aspects of our daily lives,",
        "from virtual assistants to recommendation systems. The technology continues",
        "to evolve at an unprecedented pace, bringing both opportunities and challenges.",
        "",
        "Machine learning algorithms can now process vast amounts of data to identify",
        "patterns and make predictions with remarkable accuracy. This capability has",
        "transformed industries such as healthcare, finance, and transportation.",
        "",
        "However, as AI systems become more sophisticated, questions about ethics,",
        "transparency, and human oversight become increasingly important. The future",
        "of AI development must balance innovation with responsible deployment.",
        "",
        "Looking ahead, we can expect AI to become even more integrated into our",
        "society, requiring careful consideration of its implications for employment,",
        "privacy, and human autonomy in decision-making processes."
    ]
    
    y_position = 120
    for line in content:
        if line.strip():  # Skip empty lines for spacing
            draw.text((50, y_position), line, font=font_medium, fill='black')
        y_position += 35
    
    # Add a footer
    footer = "Sample document for AI content detection testing"
    draw.text((50, height - 50), footer, font=font_small, fill='gray')
    
    # Save the image
    image.save('sample_text_image.png')
    print("Sample image with text created: sample_text_image.png")

if __name__ == "__main__":
    create_sample_image()