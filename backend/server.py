"""
House Socioeconomic Classification API
Backend for analyzing house images
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import base64
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the LLM integration
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

# ============================================
# CONFIGURATION
# ============================================
API_KEY = os.environ.get("EMERGENT_LLM_KEY")

# System prompt for house analysis
SYSTEM_PROMPT = """You are an expert socioeconomic analyst specializing in housing assessment in Indonesia.

Your task is to analyze house images and determine the likely socioeconomic status of the owner based on visual indicators.

When analyzing a house, evaluate these factors:
1. **Structure & Size**: House dimensions, number of floors, overall footprint
2. **Construction Materials**: Wood, brick, cement, quality of materials
3. **Roof Condition**: Type (tin, tile, concrete), condition, maintenance
4. **Wall Condition**: Paint, cracks, weathering, finishing quality
5. **Windows & Doors**: Quality, material, security features
6. **Surroundings**: Yard condition, fencing, landscaping
7. **Visible Amenities**: Garage, water tank, satellite dish, AC units
8. **Interior (if visible)**: Furniture, flooring, cleanliness

Based on Indonesian socioeconomic standards (Desil), classify into:
- **Low Income (Miskin)** - Desil 1-2: Basic construction, minimal amenities, signs of poverty
- **Lower-Middle Income** - Desil 3-4: Simple but maintained housing
- **Middle Income** - Desil 5-6: Standard housing with basic modern amenities
- **Upper-Middle Income** - Desil 7-8: Well-maintained, quality construction, good amenities
- **High Income (Kaya)** - Desil 9-10: Luxury construction, premium materials, extensive amenities

Always provide your response in this JSON format:
{
    "classification": "Low Income / Lower-Middle / Middle / Upper-Middle / High Income",
    "desil_range": "1-2 / 3-4 / 5-6 / 7-8 / 9-10",
    "confidence": "Low / Medium / High",
    "confidence_percentage": 85,
    "key_observations": ["observation 1", "observation 2", "observation 3"],
    "detailed_reasoning": "Full paragraph explaining the analysis..."
}

Be objective and base your analysis solely on visible evidence in the images."""


# ============================================
# FASTAPI APP
# ============================================
app = FastAPI(title="House Socioeconomic Analyzer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisResult(BaseModel):
    classification: str
    desil_range: str
    confidence: str
    confidence_percentage: int
    key_observations: List[str]
    detailed_reasoning: str


class AnalysisResponse(BaseModel):
    success: bool
    filename: str
    result: Optional[str] = None
    error: Optional[str] = None


# ============================================
# API ENDPOINTS
# ============================================

@app.get("/api/")
def root():
    return {"message": "House Socioeconomic Analyzer API is running!"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "api_key_configured": bool(API_KEY)}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_house(
    file: UploadFile = File(...),
    context: Optional[str] = Form(None)
):
    """
    Analyze a house image and return socioeconomic classification
    """
    try:
        # Validate file type
        allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: PNG, JPG, JPEG, WEBP"
            )
        
        # Read and encode image
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        # Create chat instance
        chat = LlmChat(
            api_key=API_KEY,
            session_id=f"house-analysis-{os.urandom(4).hex()}",
            system_message=SYSTEM_PROMPT
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        # Create image content
        image_content = ImageContent(image_base64=image_base64)
        
        # Build prompt
        prompt = "Please analyze this house image and determine the socioeconomic status of the owner. Return your response in the JSON format specified."
        if context:
            prompt += f"\n\nAdditional context: {context}"
        
        # Create message with image
        user_message = UserMessage(
            text=prompt,
            file_contents=[image_content]
        )
        
        # Get response
        response = await chat.send_message(user_message)
        
        return AnalysisResponse(
            success=True,
            filename=file.filename,
            result=response
        )
        
    except Exception as e:
        return AnalysisResponse(
            success=False,
            filename=file.filename if file else "unknown",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
