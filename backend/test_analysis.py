"""
Test script for House Socioeconomic Analysis
"""
import asyncio
import base64
import os
import sys
sys.path.append('/app/backend')
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

API_KEY = os.environ.get("EMERGENT_LLM_KEY")

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
    print(f"API Key present: {bool(API_KEY)}")
    
    print("\nInitializing chat with Gemini...")
    chat = LlmChat(
        api_key=API_KEY,
        session_id="test-house-analysis",
        system_message=SYSTEM_PROMPT
    )
    chat.with_model("gemini", "gemini-3-flash-preview")
    
    print("Creating message with image...")
    image_content = ImageContent(image_base64=image_base64)
    user_message = UserMessage(
        text="Please analyze this house image and determine the socioeconomic status of the owner.",
        file_contents=[image_content]
    )
    
    print("Sending to AI for analysis...")
    response = await chat.send_message(user_message)
    
    print("\n" + "="*60)
    print("ANALYSIS RESULT:")
    print("="*60)
    print(response)
    print("="*60)
    
    return response

if __name__ == "__main__":
    asyncio.run(test_analysis())
