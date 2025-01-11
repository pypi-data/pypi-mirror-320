# tests/test_watermark.py

import unittest
from inked.watermark import add_watermark
import os

class TestWatermark(unittest.TestCase):
    def test_add_image_watermark(self):
        # Provide valid paths to test with
        input_image_path = "tests/input_image.webp"
        output_image_path = "tests/output_image_with_image_watermark.jpg"
        watermark_image_path = "tests/watermark.webp"
        
        # Call add_watermark function
        add_watermark(input_image_path, output_image_path, watermark_image_path, position="center", watermark_type="image")
        
        # Ensure the output file is created
        self.assertTrue(os.path.exists(output_image_path))
    
    def test_add_text_watermark(self):
        input_image_path = "tests/input_image.webp"
        output_image_path = "tests/output_image_with_text_watermark.jpg"
        watermark_text = "Sample Watermark"
        
        add_watermark(input_image_path, output_image_path, watermark_text, position="bottom-right", watermark_type="text", font_size=30, opacity=128)
        
        self.assertTrue(os.path.exists(output_image_path))

if __name__ == "__main__":
    unittest.main()
