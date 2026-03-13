#!/usr/bin/env python3
"""
Test script to verify the AI Lead Qualification System works correctly.
Run this to test the system without making actual API calls.
"""
import json
from lead_analyzer import (
    get_analysis_prompt,
    parse_llm_response,
    create_lead_analysis,
    LeadAnalysis
)
from storage import load_leads_from_csv, format_result_for_storage


def test_prompt_generation():
    """Test that prompts are generated correctly"""
    print("Testing prompt generation...")

    sample_lead = {
        'Name': 'Test User',
        'Email': 'test@example.com',
        'Company Name': 'Test Corp',
        'Job Title': 'CEO',
        'Message from Lead': 'Looking for automation solutions'
    }

    prompt = get_analysis_prompt(sample_lead)

    assert 'Test User' in prompt
    assert 'test@example.com' in prompt
    assert 'Test Corp' in prompt
    assert 'CEO' in prompt
    assert 'automation solutions' in prompt

    print("✓ Prompt generation works correctly\n")


def test_response_parsing():
    """Test JSON response parsing"""
    print("Testing response parsing...")

    # Test valid JSON
    valid_response = json.dumps({
        "lead_score": 85,
        "industry": "Technology",
        "business_need": "Automation tools",
        "recommended_action": "Schedule demo",
        "reasoning": "High-value lead"
    })

    result = parse_llm_response(valid_response)
    assert result['lead_score'] == 85
    assert result['industry'] == "Technology"

    # Test JSON embedded in text
    text_with_json = """Here is my analysis:
    {"lead_score": 70, "industry": "Finance", "business_need": "Analytics", "recommended_action": "Call", "reasoning": "Good fit"}
    That's my assessment."""

    result = parse_llm_response(text_with_json)
    assert result['lead_score'] == 70
    assert result['industry'] == "Finance"

    print("✓ Response parsing works correctly\n")


def test_lead_analysis_creation():
    """Test LeadAnalysis object creation"""
    print("Testing lead analysis creation...")

    result = {
        "lead_score": 75,
        "industry": "SaaS",
        "business_need": "Customer support automation",
        "recommended_action": "Schedule call",
        "reasoning": "VP level, clear need"
    }

    analysis = create_lead_analysis(result)

    assert isinstance(analysis, LeadAnalysis)
    assert analysis.lead_score == 75
    assert analysis.priority == "High"  # 75 >= 70
    assert analysis.industry == "SaaS"

    # Test medium priority
    result['lead_score'] = 50
    analysis = create_lead_analysis(result)
    assert analysis.priority == "Medium"  # 50 >= 40 but < 70

    # Test low priority
    result['lead_score'] = 20
    analysis = create_lead_analysis(result)
    assert analysis.priority == "Low"  # 20 < 40

    print("✓ Lead analysis creation works correctly\n")


def test_csv_loading():
    """Test CSV file loading"""
    print("Testing CSV loading...")

    leads = load_leads_from_csv('sample_leads.csv')

    assert len(leads) > 0
    assert 'Name' in leads[0]
    assert 'Email' in leads[0]
    assert 'Company Name' in leads[0]
    assert 'Job Title' in leads[0]
    assert 'Message from Lead' in leads[0]

    print(f"✓ Loaded {len(leads)} leads from CSV\n")


def test_result_formatting():
    """Test result formatting for storage"""
    print("Testing result formatting...")

    lead = {
        'Name': 'John Doe',
        'Email': 'john@example.com',
        'Company Name': 'Acme Inc',
        'Job Title': 'CTO',
        'Message from Lead': 'Need help with AI'
    }

    analysis = LeadAnalysis(
        lead_score=82,
        industry="Technology",
        business_need="AI implementation",
        recommended_action="Schedule demo call",
        priority="High",
        reasoning="C-level executive with clear need"
    )

    result = format_result_for_storage(lead, analysis)

    assert result['Name'] == 'John Doe'
    assert result['Lead Score'] == 82
    assert result['Priority'] == 'High'
    assert 'Processed At' in result

    print("✓ Result formatting works correctly\n")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("   AI Lead Qualification System - Test Suite")
    print("=" * 50 + "\n")

    try:
        test_prompt_generation()
        test_response_parsing()
        test_lead_analysis_creation()
        test_csv_loading()
        test_result_formatting()

        print("=" * 50)
        print("   ALL TESTS PASSED!")
        print("=" * 50 + "\n")
        return True

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
