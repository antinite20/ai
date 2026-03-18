"""Test script for House Socioeconomic Analysis"""
import asyncio
import base64
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

SYSTEM_PROMPT = """You are an expert socioeconomic analyst specializing in housing assessment in Indonesia.
Analyze house images and determine the socioeconomic status. Classify into:
- Low Income (Desil 1-2)
- Lower-Middle Income (Desil 3-4)
- Middle Income (Desil 5-6)
- Upper-Middle Income (Desil 7-8)
- High Income (Desil 9-10)

Provide classification, confidence level, and reasoning."""

async def test_analysis():
    print("Loading test image...")
    with open("/tmp/test_house.png", "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')

    print(f"Image loaded. Base64 length: {len(image_base64)}")
    print(f"API Key present: {bool(GOOGLE_API_KEY)}")

    print("\nInitializing Gemini analysis...")
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = SYSTEM_PROMPT + "\n\nPlease analyze this house image and determine the socioeconomic status of the owner."

    response = model.generate_content([prompt, image_base64])

    print("\n" + "="*60)
    print("ANALYSIS RESULT:")
    print("="*60)
    print(response.text if response else "(no response)")
    print("="*60)

    return response

if __name__ == "__main__":
    asyncio.run(test_analysis())
