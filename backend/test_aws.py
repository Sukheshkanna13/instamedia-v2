import os
from dotenv import load_dotenv

load_dotenv()

from services.aws_image_generator import create_aws_image_generator

gen = create_aws_image_generator()
print("Generator:", gen)
if gen:
    print("Testing generate_and_upload...")
    try:
        res = gen.generate_and_upload("A small blue sphere on a white background, minimalist", "test_sphere.png")
        print("Result:", res)
    except Exception as e:
        print("Error generating:", type(e).__name__, str(e))
