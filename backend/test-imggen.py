import os
from openai import OpenAI
import requests

# User provided API key
OPENAI_API_KEY = ""

client = OpenAI(api_key=OPENAI_API_KEY)

try:
    print("Testing OpenAI Image Generation (DALL-E 3)...")
    response = client.images.generate(
      model="dall-e-3",
      prompt="A sleek, futuristic luxury electric bike parked in front of a modern city skyline at sunset, cyberpunk aesthetic.",
      size="1024x1024",
      quality="standard",
      n=1,
    )

    image_url = response.data[0].url
    print(f"\n✅ SUCCESS! Image generated.")
    print(f"Image URL: {image_url}")
    
    # Download the image to verify
    print("\nDownloading image...")
    img_data = requests.get(image_url).content
    with open('test_openai_image.png', 'wb') as handler:
        handler.write(img_data)
    print("✅ Image saved locally as 'test_openai_image.png'")

except Exception as e:
    print(f"\n❌ ERROR: Failed to generate image.")
    print(str(e))
