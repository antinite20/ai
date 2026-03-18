"""
Test script untuk memvalidasi sistem prompt yang sudah diupdate
Gunakan ini untuk test apakah AI menghasilkan output sesuai kategori Desil
"""

import os
import base64
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import json

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# System prompt yang sudah diupdate (sama seperti di streamlit_local.py)
SYSTEM_PROMPT = """You are an expert socioeconomic analyst specializing in housing assessment in Indonesia.

Your task is to analyze house images and classify the owner's economic status ONLY based on visual criteria below.
You MUST output ONLY valid JSON, no explanations before or after.

{
    "classification": "Low Income|Lower-Middle Income|Middle Income|Upper-Middle Income|High Income",
    "desil_range": "1-2|3-4|5-6|7-8|9-10",
    "confidence": "Low|Medium|High",
    "confidence_percentage": number_0_to_100,
    "key_observations": ["observation1", "observation2", "observation3"],
    "detailed_reasoning": "string"
}

=== DESIL 1-2 (LOW INCOME / MISKIN) ===
MUST have majority of these:
- Structure: Very small house (<25m²), 1 floor, cramped spaces
- Materials: Wood, bamboo, plastic, mud, poor bricks
- Roof: Tin with rust/leaks, plastic, missing sections, deteriorating
- Walls: Unpainted, deeply cracked, mud-based, peeling
- Condition: Signs of neglect, extreme wear, potential structural issues
- Yard: Dirt ground, no fencing, debris, overgrown
- Amenities: NO electricity meter, NO water tank, NO antenna
- Overall: Extreme poverty indicators

=== DESIL 3-4 (LOWER-MIDDLE INCOME) ===
MUST have majority of these:
- Structure: Small house (25-50m²), 1 floor
- Materials: Mix of wood and simple brick, basic blocks
- Roof: Basic tin or asbestos, some maintenance gaps
- Walls: Partially painted, minor cracks, basic finish
- Condition: Maintained but shows wear, average upkeep
- Yard: Simple paved/dirt with basic fence
- Amenities: Basic electricity present, water tank may exist
- Overall: Working class, subsistence level

=== DESIL 5-6 (MIDDLE INCOME) ===
MUST have majority of these:
- Structure: Medium house (50-100m²), 1-1.5 floors
- Materials: Quality bricks/concrete blocks, standard quality
- Roof: Ceramic or concrete tiles, well-maintained
- Walls: Well-painted, minimal cracks, good finish
- Condition: Well-maintained, clean appearance
- Yard: Properly fenced, paved ground, some landscaping
- Amenities: Electricity meter, water tank, possibly satellite dish
- Overall: Stable middle-class living

=== DESIL 7-8 (UPPER-MIDDLE INCOME) ===
MUST have majority of these:
- Structure: Large house (100-150m²+), 2 floors minimum
- Materials: Reinforced concrete, quality bricks, professional finishing
- Roof: Premium ceramic tiles or concrete, excellent condition
- Walls: Professional paint job, no visible cracks, quality finish
- Condition: Excellent maintenance, modern appearance
- Yard: Decorative fencing, landscaping, proper design
- Amenities: AC unit visible, modern gates, good outdoor lighting
- Interior: Quality furniture, good flooring (if visible)
- Overall: Professional/business owner class

=== DESIL 9-10 (HIGH INCOME / KAYA) ===
MUST have majority of these:
- Structure: Large house (150m²+), 2+ stories, spacious design
- Materials: Premium imported materials, marble/stone elements
- Roof: Luxury ceramic or imported materials, pristine condition
- Walls: Professional architectural design, perfect condition
- Condition: Luxury finishes, immaculate maintenance
- Yard: Professional landscaping, decorative elements, high-quality fence
- Amenities: Multiple AC units, solar panels, security system, driveway
- Interior: Luxury furniture, marble flooring, modern fixtures (if visible)
- Overall: Wealth indicators, luxury lifestyle

Instructions:
1. Carefully examine ALL visible details
2. Match to criteria above - must match MAJORITY of signs for each level
3. If evidence is mixed, assign MEDIUM confidence
4. If evidence is clear and matches multiple criteria, assign HIGH confidence
5. Output ONLY JSON - no text before or after"""


def test_analyze_house(image_path: str, test_name: str = ""):
    """
    Test analyze single house image
    
    Args:
        image_path: Path to test image
        test_name: Description of test (e.g., "Low Income House")
    """
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Open and encode image
        image = Image.open(image_path)
        print(f"Image loaded: {image_path}")
        print(f"Image size: {image.size}")
        
        # Generate analysis
        response = model.generate_content([
            SYSTEM_PROMPT,
            "Analyze this house image and provide ONLY JSON output.",
            image
        ])
        
        # Parse response
        response_text = response.text.strip()
        print(f"\nRaw response:\n{response_text}\n")
        
        # Try to parse JSON
        try:
            # Remove markdown code blocks if present
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = response_text
            
            result = json.loads(json_str)
            
            print("\n✅ PARSED RESULT:")
            print(f"   Classification: {result.get('classification')}")
            print(f"   Desil Range: {result.get('desil_range')}")
            print(f"   Confidence: {result.get('confidence')} ({result.get('confidence_percentage')}%)")
            print(f"   Key Observations:")
            for obs in result.get('key_observations', []):
                print(f"      - {obs}")
            print(f"   Reasoning: {result.get('detailed_reasoning')[:150]}...")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"\n❌ Failed to parse JSON: {e}")
            print("Response was not valid JSON")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None


def test_batch_analysis(image_folder: str):
    """
    Test analyze multiple images from a folder
    
    Args:
        image_folder: Path to folder containing test images
    """
    print("\n\n" + "="*70)
    print("BATCH ANALYSIS TEST")
    print("="*70)
    
    results = []
    
    # Look for image files
    import glob
    image_files = glob.glob(f"{image_folder}/*.jpg") + glob.glob(f"{image_folder}/*.png")
    
    if not image_files:
        print(f"❌ No images found in {image_folder}")
        return
    
    print(f"Found {len(image_files)} images to test\n")
    
    for i, image_path in enumerate(image_files, 1):
        filename = os.path.basename(image_path)
        result = test_analyze_house(image_path, f"Image {i}: {filename}")
        results.append({
            'filename': filename,
            'result': result
        })
    
    # Summary
    print("\n\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    desil_counts = {
        '1-2': 0,
        '3-4': 0,
        '5-6': 0,
        '7-8': 0,
        '9-10': 0,
    }
    
    confidence_levels = {
        'Low': 0,
        'Medium': 0,
        'High': 0,
    }
    
    for item in results:
        if item['result']:
            desil = item['result'].get('desil_range')
            confidence = item['result'].get('confidence')
            
            if desil in desil_counts:
                desil_counts[desil] += 1
            if confidence in confidence_levels:
                confidence_levels[confidence] += 1
    
    print("\nDesil Distribution:")
    for desil, count in desil_counts.items():
        pct = (count / len(results)) * 100 if results else 0
        print(f"   Desil {desil}: {count} images ({pct:.1f}%)")
    
    print("\nConfidence Distribution:")
    for level, count in confidence_levels.items():
        pct = (count / len(results)) * 100 if results else 0
        print(f"   {level}: {count} images ({pct:.1f}%)")
    
    return results


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║ House Socioeconomic Classifier - Prompt Validation Test         ║
    ║ Tests the updated system prompt with Desil classification       ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    Usage:
    1. Single image test:
       python test_updated_prompt.py
       (Modify image_path in code)
    
    2. Batch test:
       test_batch_analysis("path/to/images")
    
    3. Expected output: JSON with classification, desil, confidence
    """)
    
    # Example: Test single image (modify path as needed)
    # result = test_analyze_house("test_house.jpg", "Test House 1")
    
    # Example: Test batch of images
    # results = test_batch_analysis("./test_images")
    
    print("\nNote: Update the image paths and run the functions above")
    print("API Key status:", "✅ Configured" if GOOGLE_API_KEY else "❌ Not configured")
