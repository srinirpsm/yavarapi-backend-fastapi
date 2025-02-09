import google.generativeai as genai
import os
import json

# Set up Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAKAueiVVOAhwTPUrn2_hPl5WBSVowTKmY"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define Gemini Model
model = genai.GenerativeModel("gemini-pro")

# Priority Mapping
PRIORITY_KEYWORDS = {
    "urgent": "High",
    "important": "High",
    "asap": "High",
    "critical": "High",
    "normal": "Medium",
    "low": "Low"
}


def analyze_sentiment(text: str):
    try:
        prompt = f"Analyze the sentiment of this text and return a JSON response with 'label' (Positive, Neutral, Negative) and 'score' (0-1): {text}"
        response = model.generate_content(prompt)
        
        # Ensure Gemini API returns a valid JSON response
        response_json = json.loads(response.text)  # Parse response to dictionary
        return response_json
    
    except json.JSONDecodeError:
        return {"label": "Unknown", "score": 0}  # Default fallback
    
    except Exception as e:
        return {"label": "Error", "score": 0, "error": str(e)}

def suggest_priority(text: str):
    """Suggests priority based on keywords without NLTK."""
    text_lower = text.lower()
    for keyword, priority in PRIORITY_KEYWORDS.items():
        if keyword in text_lower:
            return priority
    return "Medium"  # Default priority
