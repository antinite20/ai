# House Socioeconomic Analyzer - PRD

## Problem Statement
Build an AI-powered application to analyze house images and classify the socioeconomic status of the owner based on visual indicators. Target audience: Indonesian socioeconomic analysis (using Desil classification).

## User Personas
- **Primary**: AI Engineer learners (Ruang Guru students)
- **Secondary**: Researchers conducting socioeconomic studies
- **Future**: Government agencies (requires self-hosted solution for NIK data)

## Core Requirements
- Upload house images (PNG, JPG, JPEG, WEBP)
- AI-powered analysis using vision models
- Classification into Indonesian Desil categories (1-10)
- Detailed reasoning with confidence level
- Simple, editable Python + Streamlit code

## Architecture
- **Frontend/App**: Streamlit (Python)
- **AI Model**: Gemini 3 Flash (via Emergent LLM Key)
- **Port**: 8501

## What's Been Implemented (Jan 2026)
- [x] Streamlit app with image upload
- [x] Multi-image support with preview
- [x] Gemini Vision AI integration
- [x] Detailed analysis output (classification + reasoning)
- [x] Sidebar with app info and tips
- [x] Additional context input field
- [x] Test script for CLI testing
- [x] All tests passed (100%)

## Files Created
- `/app/backend/streamlit_app.py` - Main Streamlit application
- `/app/backend/test_analysis.py` - CLI test script
- `/app/backend/run_streamlit.sh` - Run script
- `/app/image_testing.md` - Testing guidelines

## Classification Categories
| Category | Desil | Description |
|----------|-------|-------------|
| Low Income | 1-2 | Basic construction, minimal amenities |
| Lower-Middle | 3-4 | Simple but maintained housing |
| Middle Income | 5-6 | Standard housing with basic modern amenities |
| Upper-Middle | 7-8 | Well-maintained, quality construction |
| High Income | 9-10 | Luxury construction, premium materials |

## Backlog / Future Enhancements
### P0 (Next Priority)
- [ ] Self-hosted version with open-source model (LLaVA/Moondream)
- [ ] Google Colab notebook for local deployment

### P1
- [ ] Batch processing for multiple houses
- [ ] Export results to CSV/PDF
- [ ] History of analyzed images

### P2
- [ ] Map integration for location context
- [ ] Comparison tool between houses
- [ ] Training data collection interface

## Self-Hosted Options (For Confidential Data)
For government/NIK data that cannot be sent to external APIs:
- **LLaVA**: Open-source vision model
- **Moondream**: Lightweight, can run on CPU
- **Deployment**: Google Colab, own server, Indonesian cloud (Biznet/Telkom)

## Cost Analysis
| Usage | Model | Monthly Cost |
|-------|-------|--------------|
| 100 images/day | Gemini Flash | ~$6/month |
| 100 images/day | GPT-4o-mini | ~$12/month |
| Self-hosted | Open Source | Server cost only |
