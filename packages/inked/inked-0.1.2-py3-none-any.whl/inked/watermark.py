import argparse
from typing import Any, Union
from PIL import Image, ImageDraw, ImageFont

def get_predefined_position(image_size: tuple[int, int], watermark_size: tuple[int, int], position: str) -> tuple[int, int]:
    """
    Calculates the position of the watermark based on predefined positions.
    
    :param image_size: Tuple (width, height) of the image.
    :param watermark_size: Tuple (width, height) of the watermark.
    :param position: Predefined position string ('top-left', 'center', 'bottom-right').
    :return: (x, y) tuple for the watermark position.
    """
    image_width, image_height = image_size
    watermark_width, watermark_height = watermark_size
    
    if position == "center":
        return (image_width - watermark_width) // 2, (image_height - watermark_height) // 2
    elif position == "bottom-right":
        return image_width - watermark_width - 10, image_height - watermark_height - 10
    elif position == "top-left":
        return 10, 10
    else:
        raise ValueError("Invalid predefined position. Use 'center', 'bottom-right', or 'top-left'.")

def add_watermark(
    input_image_path: str,
    output_image_path: str,
    watermark_data: str,
    position: Union[str, tuple[int, int]] = "bottom-right",
    watermark_type: str = "image",
    font_size: int = 30,
    opacity: int = 128
) -> None:
    """
    Adds a watermark (image or text) to an image at a custom or predefined position.

    :param input_image_path: Path to the input image.
    :param output_image_path: Path to save the output image with watermark.
    :param watermark_data: Path to the watermark image or the text for watermarking.
    :param position: Position for the watermark ('top-left', 'center', 'bottom-right' or custom (x, y)).
    :param watermark_type: Type of watermark ('image' or 'text').
    :param font_size: Font size for text watermark.
    :param opacity: Opacity of the watermark (0 to 255).
    """
    try:
        # Open the image
        image = Image.open(input_image_path).convert("RGBA")
        image_width, image_height = image.size

        # Handle image watermark
        if watermark_type == 'image':
            watermark = Image.open(watermark_data).convert("RGBA")
            watermark_width, watermark_height = watermark.size

            # If position is a string, use predefined logic
            if isinstance(position, str):
                position = get_predefined_position(image.size, watermark.size, position)

            # Resize watermark if needed (optional, based on original image size)
            scale_factor = 0.1  # Resize watermark to 10% of image width (adjust if needed)
            new_width = int(image_width * scale_factor)
            new_height = int(watermark_height * (new_width / watermark_width))
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Apply opacity to watermark
            watermark_with_opacity = watermark.copy()
            watermark_with_opacity.putalpha(opacity)

            # Paste watermark onto the image
            image.paste(watermark_with_opacity, position, watermark_with_opacity)

        # Handle text watermark
        elif watermark_type == 'text':
            watermark_text = watermark_data
            draw = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

            # Calculate text size using textbbox
            text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

            # If position is a string, use predefined logic
            if isinstance(position, str):
                position = get_predefined_position(image.size, (text_width, text_height), position)

            # Apply opacity to text
            watermark_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
            watermark_draw = ImageDraw.Draw(watermark_overlay)
            watermark_draw.text(position, watermark_text, font=font, fill=(255, 255, 255, opacity))

            # Combine image with text watermark
            image = Image.alpha_composite(image, watermark_overlay)

        else:
            raise ValueError("Invalid watermark type. Use 'image' or 'text'.")

        # Save the final image with watermark
        image.save(output_image_path, "PNG")
        print(f"Watermarked image saved to {output_image_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Add a watermark (text or image) to an image.")
    
    # Define command-line arguments
    parser.add_argument("input_image", help="Path to the input image.")
    parser.add_argument("output_image", help="Path to save the output image with the watermark.")
    parser.add_argument("watermark_data", help="Path to the watermark image or the text for watermarking.")
    parser.add_argument("--position", default="bottom-right", choices=["top-left", "center", "bottom-right"],
                        help="Position of the watermark (default: bottom-right).")
    parser.add_argument("--watermark_type", default="image", choices=["image", "text"],
                        help="Type of watermark: 'image' or 'text' (default: image).")
    parser.add_argument("--font_size", type=int, default=30, help="Font size for text watermark (default: 30).")
    parser.add_argument("--opacity", type=int, default=128, choices=range(0, 256),
                        help="Opacity for the watermark (default: 128).")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the add_watermark function with the parsed arguments
    add_watermark(
        input_image_path=args.input_image,
        output_image_path=args.output_image,
        watermark_data=args.watermark_data,
        position=args.position,
        watermark_type=args.watermark_type,
        font_size=args.font_size,
        opacity=args.opacity
    )

if __name__ == "__main__":
    main()

