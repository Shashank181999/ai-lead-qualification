"""
AI Lead Analysis Module
Uses LLM to analyze and score leads
"""
import json
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
import config


@dataclass
class LeadAnalysis:
    """Structured result from lead analysis"""
    lead_score: int
    industry: str
    business_need: str
    recommended_action: str
    priority: str
    reasoning: str


def get_analysis_prompt(lead: Dict[str, str]) -> str:
    """Generate the prompt for lead analysis"""
    return f"""You are an expert sales lead qualification specialist. Analyze the following lead and provide a detailed qualification assessment.

Lead Information:
- Name: {lead.get('Name', 'N/A')}
- Email: {lead.get('Email', 'N/A')}
- Company: {lead.get('Company Name', 'N/A')}
- Job Title: {lead.get('Job Title', 'N/A')}
- Message: {lead.get('Message from Lead', 'N/A')}

Analyze this lead and provide your assessment in the following JSON format:
{{
    "lead_score": <number between 0-100>,
    "industry": "<industry category>",
    "business_need": "<brief description of their business need>",
    "recommended_action": "<specific action for sales team>",
    "reasoning": "<brief explanation of the score>"
}}

Scoring Guidelines:
- 80-100: Hot lead - Decision maker, clear budget, immediate need, large company
- 60-79: Warm lead - Good fit, some buying signals, worth pursuing
- 40-59: Moderate lead - Potential fit but needs nurturing
- 20-39: Cool lead - Low priority, unclear fit
- 0-19: Cold/Invalid - Spam, test submissions, or no business potential

Consider these factors:
1. Job title seniority (C-level, VP, Director = higher score)
2. Company size indicators
3. Clarity and specificity of the message
4. Budget indicators
5. Urgency signals
6. Industry fit

Respond ONLY with the JSON object, no additional text."""


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """Parse LLM response to extract JSON"""
    try:
        # Try direct JSON parsing
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

    # Return default values if parsing fails
    return {
        "lead_score": 0,
        "industry": "Unknown",
        "business_need": "Unable to analyze",
        "recommended_action": "Manual review required",
        "reasoning": "Failed to parse AI response"
    }


def analyze_with_openai(lead: Dict[str, str]) -> LeadAnalysis:
    """Analyze lead using OpenAI API"""
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a lead qualification expert. Always respond with valid JSON only."},
            {"role": "user", "content": get_analysis_prompt(lead)}
        ],
        temperature=0.3,
        max_tokens=500
    )

    result = parse_llm_response(response.choices[0].message.content)
    return create_lead_analysis(result)


def analyze_with_anthropic(lead: Dict[str, str]) -> LeadAnalysis:
    """Analyze lead using Anthropic Claude API"""
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=500,
        messages=[
            {"role": "user", "content": get_analysis_prompt(lead)}
        ]
    )

    result = parse_llm_response(response.content[0].text)
    return create_lead_analysis(result)


def analyze_with_groq(lead: Dict[str, str]) -> LeadAnalysis:
    """Analyze lead using Groq API"""
    from groq import Groq

    client = Groq(api_key=config.GROQ_API_KEY)

    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a lead qualification expert. Always respond with valid JSON only."},
            {"role": "user", "content": get_analysis_prompt(lead)}
        ],
        temperature=0.3,
        max_tokens=500
    )

    result = parse_llm_response(response.choices[0].message.content)
    return create_lead_analysis(result)


def create_lead_analysis(result: Dict[str, Any]) -> LeadAnalysis:
    """Create LeadAnalysis object from parsed result"""
    score = int(result.get("lead_score", 0))

    # Determine priority based on score
    if score >= config.HIGH_PRIORITY_THRESHOLD:
        priority = "High"
    elif score >= config.MEDIUM_PRIORITY_THRESHOLD:
        priority = "Medium"
    else:
        priority = "Low"

    return LeadAnalysis(
        lead_score=score,
        industry=result.get("industry", "Unknown"),
        business_need=result.get("business_need", "Not specified"),
        recommended_action=result.get("recommended_action", "Manual review"),
        priority=priority,
        reasoning=result.get("reasoning", "")
    )


def analyze_lead(lead: Dict[str, str]) -> LeadAnalysis:
    """Main function to analyze a lead using configured LLM provider"""
    provider = config.LLM_PROVIDER.lower()

    try:
        if provider == "openai":
            return analyze_with_openai(lead)
        elif provider == "anthropic":
            return analyze_with_anthropic(lead)
        elif provider == "groq":
            return analyze_with_groq(lead)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    except Exception as e:
        print(f"Error analyzing lead {lead.get('Name', 'Unknown')}: {str(e)}")
        return LeadAnalysis(
            lead_score=0,
            industry="Error",
            business_need="Analysis failed",
            recommended_action="Manual review required",
            priority="Low",
            reasoning=f"Error: {str(e)}"
        )
