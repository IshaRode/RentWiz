"""
RentWiz – AI Explanation Service
Uses Google Gemini API to generate natural language deal explanations.
Gracefully falls back to template strings if API key is not set.
"""
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

_gemini_model = None


def _init_gemini():
    """Lazily initialise the Gemini client."""
    global _gemini_model
    if not settings.gemini_api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("✅ Gemini AI client ready")
    except Exception as e:
        logger.warning(f"⚠️  Could not init Gemini: {e}")
    return _gemini_model


def generate_explanation(
    city: str,
    bhk: int,
    area_sqft: int,
    actual_rent: int,
    predicted_rent: int,
    deal_score: int,
    deal_label: str,
    location: str = "",
) -> str:
    """
    Generate a plain-English explanation for the deal quality.
    Tries Gemini first, falls back to template.
    """
    if settings.use_ai_explanations and settings.gemini_api_key:
        try:
            model = _gemini_model or _init_gemini()
            if model:
                return _gemini_explanation(
                    model, city, bhk, area_sqft,
                    actual_rent, predicted_rent, deal_score, deal_label, location
                )
        except Exception as e:
            logger.warning(f"Gemini call failed, using template: {e}")

    return _template_explanation(
        city, bhk, area_sqft, actual_rent, predicted_rent, deal_score, deal_label, location
    )


def _gemini_explanation(model, city, bhk, area_sqft, actual_rent, predicted_rent,
                         deal_score, deal_label, location) -> str:
    loc_str = f" in {location}," if location else ","
    prompt = f"""You are a real estate analyst explaining a rental deal to an Indian renter.

Property: {bhk}BHK, {area_sqft} sq ft{loc_str} {city}
Actual Rent: ₹{actual_rent:,}/month
Fair Market Rent (predicted): ₹{predicted_rent:,}/month
Deal Score: ₹{deal_score:,} ({'underpriced' if deal_score > 0 else 'overpriced'})
Classification: {deal_label.replace('_', ' ').title()}

Write ONE concise sentence (max 30 words) explaining this deal to the renter. Be specific about the amount and be encouraging or cautionary as appropriate. Do not use markdown."""

    response = model.generate_content(prompt)
    return response.text.strip()


def _template_explanation(city, bhk, area_sqft, actual_rent, predicted_rent,
                           deal_score, deal_label, location) -> str:
    loc_str = f" in {location}," if location else ","
    diff = abs(deal_score)
    pct = round(abs(deal_score) / predicted_rent * 100) if predicted_rent else 0

    if deal_label == "good_deal":
        return (
            f"This {bhk}BHK{loc_str} {city} is priced ₹{diff:,}/month below the "
            f"fair market rate — that's {pct}% below similar properties in the area."
        )
    elif deal_label == "overpriced":
        return (
            f"This {bhk}BHK{loc_str} {city} is listed ₹{diff:,}/month above "
            f"comparable properties — consider negotiating or exploring nearby options."
        )
    else:
        return (
            f"This {bhk}BHK{loc_str} {city} is fairly priced within ₹{diff:,}/month "
            f"of the predicted market rent for similar properties."
        )
